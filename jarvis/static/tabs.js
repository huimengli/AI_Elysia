(function () {
  // 三页共用一份顶栏（design v3.2 §3-5）：不在每页手写，避免三份漂移。当前页高亮，真跳转。
  var tabs = [["/", "主界面"], ["/monitor", "monitor（监视界面）"], ["/about", "about（相关页面）"]];
  var bar = document.createElement("div");
  bar.className = "dsh-tabs";
  var path = location.pathname.replace(/\/+$/, "") || "/";
  tabs.forEach(function (t) {
    var a = document.createElement("a");
    a.href = t[0]; a.textContent = t[1];
    if ((t[0].replace(/\/+$/, "") || "/") === path) a.className = "active";
    bar.appendChild(a);
  });
  document.body.insertBefore(bar, document.body.firstChild);
})();
