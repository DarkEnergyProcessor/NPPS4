function Tab(tabs, options) {
  this.map = {};

  Array.prototype.forEach.call(tabs, function (tab) {
    var targetId = Tab._getTargetId(tab);
    var target = document.getElementById(targetId);

    this.map[targetId] = {tab: tab, target: target};

    Button.initialize(tab, function () {
      if (tab.classList.contains('disabled')) return;
      this.show(targetId);
    }.bind(this));
  }, this);

  this.options = options || {};

  var initial = this.map[this.options.initialTargetId]
    ? this.options.initialTargetId
    : Tab._getTargetId(tabs[0]);

  this.show(initial);
}

Tab._getTargetId = function (tab) {
  return tab.getAttribute('data-target-id');
};

Tab.prototype.show = function (targetId) {
  Object.keys(this.map).forEach(function (id) {
    var entry = this.map[id];

    if (id === targetId) {
      entry.tab.classList.add('active');
      entry.target.style.display = 'block';
    } else {
      entry.tab.classList.remove('active');
      entry.target.style.display = 'none';
    }
  }, this);

  if (typeof this.options.onShow === 'function') {
    this.options.onShow(targetId);
  }
};
