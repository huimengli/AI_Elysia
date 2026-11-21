(function () {
  // 三页共用一份顶栏（design v3.2 §3-5，v3.3 标签全中文、外观仿 Chrome 标签页）。
  // 路由名不变（/ /monitor /about），只改显示文字；当前页高亮由 location.pathname 决定，真跳转。
  var tabs = [["/", "主界面", "#F8A9C4"], ["/monitor", "监视界面", "#C9B7E0"], ["/about", "相关页面", "#F2C9A8"]];
  var bar = document.createElement("div");
  bar.className = "dsh-tabs";
  var path = location.pathname.replace(/\/+$/, "") || "/";
  tabs.forEach(function (t) {
    var a = document.createElement("a");
    a.href = t[0];
    var dot = document.createElement("span");
    dot.className = "dot";
    dot.style.background = t[2];
    a.appendChild(dot);
    a.appendChild(document.createTextNode(t[1]));
    if ((t[0].replace(/\/+$/, "") || "/") === path) a.className = "active";
    bar.appendChild(a);
  });
  document.body.insertBefore(bar, document.body.firstChild);
})();
