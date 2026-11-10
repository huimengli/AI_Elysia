import subprocess
import os
import threading
import time

_VOL_TYPE = """
using System.Runtime.InteropServices;
[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioEndpointVolume {
    void _a();void _b();void _c();void _d();
    int SetMasterVolumeLevelScalar(float f, System.Guid g);
    void _f();
    int GetMasterVolumeLevelScalar(out float f);
}
[Guid("D666063F-1587-4E43-81F1-B948E807363F"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDevice {
    int Activate(ref System.Guid id,int c,System.IntPtr p,[MarshalAs(UnmanagedType.IUnknown)]out object o);
}
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumerator {
    void _a();
    int GetDefaultAudioEndpoint(int flow,int role,out IMMDevice dev);
}
[ComImport,Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
public class MMDeviceEnumerator {}
"""


def _run_vol_ps(ps: str) -> subprocess.CompletedProcess:
    return subprocess.run(["powershell", "-command", ps], capture_output=True, text=True)


def set_volume(level: int) -> str:
    """Set system volume (0-100) via Windows Audio API."""
    level = max(0, min(100, level))
    scalar = level / 100.0
    ps = (
        f"Add-Type -TypeDefinition @'\n{_VOL_TYPE}\n'@ -Language CSharp 2>$null;"
        "$e = [MMDeviceEnumerator] -as [IMMDeviceEnumerator];"
        "$d = $null; $e.GetDefaultAudioEndpoint(0,1,[ref]$d);"
        "$g = [System.Guid]'5CDF2C82-841E-4546-9722-0CF74078229A';"
        "$v = $null; $d.Activate([ref]$g,1,[IntPtr]::Zero,[ref]$v);"
        f"$v.SetMasterVolumeLevelScalar({scalar},[System.Guid]::Empty)"
    )
    _run_vol_ps(ps)
    return f"音量已设为 {level}%。"


def get_volume() -> str:
    """Get current system volume (0-100)."""
    ps = (
        f"Add-Type -TypeDefinition @'\n{_VOL_TYPE}\n'@ -Language CSharp 2>$null;"
        "$e = [MMDeviceEnumerator] -as [IMMDeviceEnumerator];"
        "$d = $null; $e.GetDefaultAudioEndpoint(0,1,[ref]$d);"
        "$g = [System.Guid]'5CDF2C82-841E-4546-9722-0CF74078229A';"
        "$v = $null; $d.Activate([ref]$g,1,[IntPtr]::Zero,[ref]$v);"
        "$f = 0.0; $v.GetMasterVolumeLevelScalar([ref]$f); [int]($f*100)"
    )
    result = _run_vol_ps(ps)
    vol = result.stdout.strip()
    return f"当前音量 {vol}%。" if vol.isdigit() else "读不到音量。"


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
