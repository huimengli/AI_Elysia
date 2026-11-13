import subprocess
import os
import threading
import time

# Add-Type 的 CodeDom 编译目录，必须落在工作区内（服务在 harness 后台任务里
# 跑时 %TEMP% 禁写，见 HB-033 延伸）。
_PS_TEMP = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), ".tmp", "pscompile")

_VOL_TYPE = """
using System;
using System.Runtime.InteropServices;

[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E"), ClassInterface(ClassInterfaceType.None)]
public class MMDeviceEnumerator { }

[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioEndpointVolume {
    int _a(); int _b(); int _c(); int _d();
    int SetMasterVolumeLevelScalar(float f, System.Guid g);
    int _f();
    int GetMasterVolumeLevelScalar(out float pf);
}

[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDevice {
    int Activate(ref System.Guid id, int c, System.IntPtr p, [MarshalAs(UnmanagedType.IUnknown)] out object o);
}

[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumerator {
    int _a();
    int GetDefaultAudioEndpoint(int flow, int role, out IMMDevice dev);
}

public static class AudioVol {
    static IMMDeviceEnumerator Enum() { return (IMMDeviceEnumerator)(new MMDeviceEnumerator()); }
    static IAudioEndpointVolume Ep(int role) {
        IMMDevice d;
        int rc = Enum().GetDefaultAudioEndpoint(0, role, out d);
        if (rc != 0 || d == null) return null;
        object o;
        System.Guid g = new System.Guid("5CDF2C82-841E-4546-9722-0CF74078229A");
        int rca = d.Activate(ref g, 1, System.IntPtr.Zero, out o);
        if (rca != 0) return null;
        return (IAudioEndpointVolume)o;
    }
    public static int Get(int role) {
        var v = Ep(role);
        if (v == null) return -1;
        float f;
        return v.GetMasterVolumeLevelScalar(out f) == 0 ? (int)Math.Round(f * 100) : -1;
    }
    public static int Set(int level, int role) {
        var v = Ep(role);
        if (v == null) return -1;
        v.SetMasterVolumeLevelScalar(level / 100.0f, System.Guid.Empty);
        float f;
        v.GetMasterVolumeLevelScalar(out f);
        return (int)Math.Round(f * 100);
    }
}
"""


def _vol_ps(ps: str) -> subprocess.CompletedProcess:
    """Run PowerShell with Add-Type compiling inside the workspace.

    HB-033 的延伸：`Add-Type -TypeDefinition` 要把源码写进 `%TEMP%`（CodeDom 编译），
    而服务作为 harness 后台任务启动时，python 子进程的 `%TEMP%` 是**禁写**的
    （`Access to the path 'C:\\Users\\...\\AppData\\Local\\Temp\\xxx.tmp' is denied`，
    12:25:43 那次「把音量调到60」就死在这里）。所以把 `$env:TEMP` 指到工作区内的
    `.tmp/pscompile`，Add-Type 就能编译。实测：重定向前 rc=1 且被拒，重定向后
    rc=0、`[AudioVol]::Get(0)` → 20（`training/_t3_temp_probe.py`）。
    """
    os.makedirs(_PS_TEMP, exist_ok=True)
    redirect = f"$env:TEMP='{_PS_TEMP}'; $env:TMP=$env:TEMP; "
    return subprocess.run(["powershell", "-NoProfile", "-command", redirect + ps],
                          capture_output=True, text=False, timeout=20)


def _read_volume() -> int:
    """Read master volume of the multimedia endpoint (0-100), -1 on failure.

    HB-033：以前读的是 `GetDefaultAudioEndpoint(0,1)` = `eConsole` 端点，跟播放器
    看到的音量不是同一条（读数恒 0%，你看到的实际是 20%）。现在用 `role=0`
    （`eMultimedia`），且用 C# 类里的 COM 激活 —— 老的 `[MMDeviceEnumerator] -as
    [IMMDeviceEnumerator]` 写法在 PowerShell 里**返回 null**，整条调用链打在 null 上，
    stdout 为空。
    """
    r = _vol_ps("Add-Type -TypeDefinition @'\n" + _VOL_TYPE + "\n'@ -Language CSharp;"
                "[AudioVol]::Get(0)")
    out = r.stdout.decode("utf-8", errors="ignore").strip()
    return int(out) if out.lstrip("-").isdigit() else -1


def set_volume(level: int) -> str:
    """Set system volume (0-100) and **verify by reading it back**.

    HB-033（2026-11-13，`tests/2026-11-08-20-44-17_cc/record_9.md`）：老实现跑完
    PowerShell 不检查 returncode、不检查输出，无条件 `return "音量已设为 X%。"`，
    于是「把音量调大」回复「已调至最大 (100%)」而设备仍是 20% —— 模型拿不到失败
    信号，2026-11-08 治理的「工具失败要直说」被工具本身架空。现在复读音量作为证据，
    读数与目标不符就返回失败，并把 stdout/stderr 带进回复。
    """
    level = max(0, min(100, level))
    r = _vol_ps("Add-Type -TypeDefinition @'\n" + _VOL_TYPE + "\n'@ -Language CSharp;"
                f"[AudioVol]::Set({level}, 0)")
    out = r.stdout.decode("utf-8", errors="ignore").strip()
    err = r.stderr.decode("utf-8", errors="ignore").strip()
    readback = int(out) if out.lstrip("-").isdigit() else -1
    if r.returncode == 0 and abs(readback - level) <= 2:
        return f"音量已设为 {readback}%（已复读确认）。"
    return f"音量设置失败（目标 {level}%，复读 {readback}%）：{err or out or '无输出'}"


def get_volume() -> str:
    """Get current system volume (0-100)."""
    vol = _read_volume()
    return f"当前音量 {vol}%。" if vol >= 0 else "读不到音量。"


def _ps_utf8(args: list[str]) -> str:
    """Run PowerShell and decode its stdout as UTF-8.

    With `text=True` the bytes were decoded with the local code page, so the
    Chinese labels in get_system_info came back as mojibake (round 1 of
    records/2026-11-10-17-43-08.md: `CPU 21% | 鍐呭瓨 宸茬敤 …`).
    """
    result = subprocess.run(args, capture_output=True, text=False)
    return result.stdout.decode("utf-8", errors="ignore").strip()


def get_clipboard() -> str:
    """Return current clipboard text."""
    return _ps_utf8(["powershell", "-command", "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; Get-Clipboard"])


def set_clipboard(text: str) -> str:
    """Set clipboard content."""
    safe = text.replace("'", "''")
    subprocess.run(
        ["powershell", "-command", f"Set-Clipboard -Value '{safe}'"],
        capture_output=True,
    )
    return "剪贴板已更新。"


def get_system_info() -> str:
    """Get CPU, RAM, and disk usage."""
    ps = (
        "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
        "$cpu = (Get-CimInstance Win32_Processor).LoadPercentage;"
        "$os = Get-CimInstance Win32_OperatingSystem;"
        "$ram_total = [math]::Round($os.TotalVisibleMemorySize/1MB,1);"
        "$ram_free = [math]::Round($os.FreePhysicalMemory/1MB,1);"
        "$ram_used = $ram_total - $ram_free;"
        "$disk = Get-CimInstance Win32_LogicalDisk -Filter 'DeviceID=\"C:\"';"
        "$disk_total = [math]::Round($disk.Size/1GB,1);"
        "$disk_free = [math]::Round($disk.FreeSpace/1GB,1);"
        "Write-Output \"CPU ${cpu}% | 内存 已用 ${ram_used}/${ram_total} GB | "
        "磁盘C 剩余 ${disk_free}/${disk_total} GB\""
    )
    return _ps_utf8(["powershell", "-command", ps]) or "读不到系统信息。"


def set_brightness(level: int) -> str:
    """Set screen brightness (0-100). Only works on laptops."""
    level = max(0, min(100, level))
    ps = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
    result = subprocess.run(["powershell", "-command", ps], capture_output=True, text=True)
    if result.returncode == 0:
        return f"亮度已设为 {level}%。"
    return "这台台式机不支持通过 WMI 调节亮度。"


def lock_screen() -> str:
    """Lock the workstation."""
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    return "已锁定屏幕。"


def power_command(action: str) -> str:
    """Shutdown, restart, or sleep the PC."""
    action = action.lower().strip()
    if action == "shutdown":
        subprocess.Popen(["shutdown", "/s", "/t", "5"])
        return "5 秒后关机。"
    elif action == "restart":
        subprocess.Popen(["shutdown", "/r", "/t", "5"])
        return "5 秒后重启。"
    elif action == "sleep":
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
        return "已进入睡眠。"
    return f"未知电源操作：{action}，请用 shutdown/restart/sleep。"


def show_notification(title: str, message: str) -> str:
    """Show a Windows toast notification."""
    safe_title = title.replace("'", "''")
    safe_msg = message.replace("'", "''")
    ps = (
        "[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime] > $null;"
        "$xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent(1);"
        "$text = $xml.GetElementsByTagName('text');"
        f"$text[0].AppendChild($xml.CreateTextNode('{safe_title}')) > $null;"
        f"$text[1].AppendChild($xml.CreateTextNode('{safe_msg}')) > $null;"
        "$toast = [Windows.UI.Notifications.ToastNotification]::new($xml);"
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('爱莉希雅').Show($toast)"
    )
    result = subprocess.run(["powershell", "-command", ps], capture_output=True, text=True)
    if result.returncode == 0:
        return f"已弹出通知：{title}"
    return f"通知失败：{result.stderr.strip()}"


# --- Timer / Reminder ---
_timers: list = []


def set_timer(seconds: int, message: str = "定时到了！") -> str:
    """Set a timer that shows a notification after N seconds."""
    def _timer_cb():
        show_notification("爱莉希雅定时提醒", message)

    t = threading.Timer(seconds, _timer_cb)
    t.daemon = True
    t.start()
    _timers.append(t)

    if seconds >= 3600:
        time_str = f"{seconds // 3600}小时 {(seconds % 3600) // 60}分"
    elif seconds >= 60:
        time_str = f"{seconds // 60}分 {seconds % 60}秒"
    else:
        time_str = f"{seconds}秒"
    return f"已设置 {time_str} 后的提醒：{message}"


def get_time() -> str:
    """Current local date, clock time and weekday — for 现在几点 / 今天几号.

    The 2B model answered 现在几点 with a get_weather call (user test
    2026-11-08-19-52-59, records/2026-11-08-19-25-48.md), so there needs to be a
    tool it can map the question to.
    """
    import datetime
    now = datetime.datetime.now()
    wd = "一二三四五六日"[now.weekday()]
    return f"{now.strftime('%Y-%m-%d %H:%M:%S')} 星期{wd}"
