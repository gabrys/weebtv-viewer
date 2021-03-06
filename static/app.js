var $body = $('body'),
  $channels,
  $channelsSection = $('#channel-list'),
  $player = $('#player'),
  $settings = $('#settings'),
  $settingButtons = $settings.find('button'),
  $settingFlash = $settingButtons.filter('[name="flash"]'),
  $settingHd = $settingButtons.filter('[name="hd"]'),
  settingFlash = getSetting('flash', false),
  settingHd = getSetting('hd', true),
  mode = 'channels',
  style = '',
  progName = location.href.toString().split('/')[6],
  $progLink,
  premium,
  fullscreenTimeout,
  clickTimeout;

// FUNCTIONS

function scrollChannelListToLink($progLink) {
  var $progItem = $progLink.parents('li').first(),
    scroll;

  scroll = $progItem.position().top - window.innerHeight / 2 + $progItem.height() / 2;
  $channels.scrollTop($channels.scrollTop() + scroll);

  if (clickTimeout) {
    clearTimeout(clickTimeout);
  }
  clickTimeout = setTimeout(function () {
    $player.attr('src', $progLink.attr('href'));
  }, 200);
}

function channelDown() {
  var $progLink = $channels.find('.current').next().find('a');
  if ($progLink.length === 0) {
    $progLink = $channels.find('li').eq(1).find('a');
  }
  $progLink.trigger('click');
}

function channelUp() {
  var $progLink = $channels.find('.current').prev().find('a');
  if ($progLink.length === 0) {
    $progLink = $channels.find('li').last().find('a');
  }
  $progLink.trigger('click');
}

function flashMessage(type, msg, time) {
  var $msg = $('<div></div>').addClass(type).text(msg).hide();
  $('#messages').append($msg);
  $msg.fadeIn();
  setTimeout(function () { $msg.fadeOut(); }, time);
}

function clickChannel() {
  var $this = $(this);
  location.hash = $this.attr('id').replace('link-', '#play-');
  $channels.find('.current').removeClass('current');
  $this.parent().addClass('current');
  $player.show();
  $body.attr('class', 'both');
  scrollChannelListToLink($this);
  if (fullscreenTimeout) {
    clearTimeout(fullscreenTimeout);
  }
  fullscreenTimeout = setTimeout(handleFullscreen, 10000);
  return false;
}

function buildChannelList() {
  // CHANNEL LIST

  var i, len, oldScrollTop, $newChannels = $('<ul></ul>');
  for (i = 0, len = WeebTvChannels.length; i < len; i += 1) {
    var ch = WeebTvChannels[i],
      title = ch.channel_title,
      chName = ch.channel_name,
      chThumb = ch.channel_thumbnail_url,
      chLogo = ch.channel_logo_url,
      isHd = settingHd && (ch.multibitrate === '1'),
      chHrefRtmp = '/player/' + ch.cid + (isHd ? '/hd.html' : '/sd.html'),
      chHrefFlash = 'http://weeb.tv/mini-channel/' + chName,
      chHref = settingFlash ? chHrefFlash : chHrefRtmp,
      $chLogo = $('<img alt="" class="logo"/>').attr('src', chLogo),
      $chThumb = $('<img alt="" class="thumb"/>').attr('src', chLogo),
      $chLink = $('<a target="player"/>').attr('id', 'link-' + chName).attr('href', chHref).on('click', clickChannel);
      $newCh = $('<li></li>');

    $newCh.append($chThumb);
    $newCh.append($chLogo);
    $newCh.wrapInner($chLink);

    $newChannels.append($newCh);
  }
  updateThumbs($newChannels);

  $newChannels.prepend($('<li id="go-to-grid"><a href="."><img src="/static/grid.png" alt="grid"></a></li>'));

  oldScrollTop = $channels && $channels.scrollTop();
  currentLink = $channels && $channels.find('.current a').attr('id');

  $channelsSection.html($newChannels);
  $newChannels.scrollTop(oldScrollTop);
  $newChannels.find('#' + currentLink).parent().addClass('current');

  $channels = $newChannels;
}

function handleHash() {
  if (location.hash.match(/^#play-/)) {
    $link = $(location.hash.replace('#play-', '#link-'));
    $link.trigger('click');
  }
}

function updateThumbs($where) {
  var chName;
  $where = $where || $body;
  if (!window.WeebTvThumbs && localStorage.WeebTvThumbs) {
    WeebTvThumbs = JSON.parse(localStorage.WeebTvThumbs);
  }
  if (window.WeebTvThumbs) {
    for (chName in WeebTvThumbs) {
      $('#link-' + chName, $where).find('.thumb').attr('src', WeebTvThumbs[chName]);
    }
    setTimeout(function () {
      localStorage.WeebTvThumbs = JSON.stringify(WeebTvThumbs);
    }, 0);
  }
}

function updatePremium(newPremium) {
  if (newPremium !== premium) {
    premium = newPremium;
    if (premium) {
      flashMessage('success', 'Premium account', 3000);
    } else {
      flashMessage('error', 'No premium account', 3000);
    }
  }
}

function setSetting(name, value) {
  var key = 'WeebTv_' + name;
  localStorage[key] = JSON.stringify(value);
}

function getSetting(name, def) {
  var undef,
      key = 'WeebTv_' + name;

  if (localStorage[key]) {
    return JSON.parse(localStorage[key]);
  }

  return def;
}

function handleSettings() {
  $settingButtons.on('click', function () {
    var name, value;
    $(this).toggleClass('on');
    name = $(this).attr('name');
    value = $(this).hasClass('on');

    if (name === 'open') {
      $settings.toggleClass('open');
    } else {
      setSetting(name, value);
      location.reload();
    }
  });

  if (settingHd) {
    $settingHd.addClass('on');
  }

  if (settingFlash) {
    $settingFlash.addClass('on');
    $settingHd.hide();
  }
}

function handleFullscreen() {
  var diff = window.outerHeight - window.innerHeight,
    fullscreen = diff < 5;
  if (fullscreen) {
    $body.addClass('fullscreen');
  } else {
    $body.removeClass('fullscreen');
  }
}

function handleKeyboard() {
  $(document).on('keydown', function (e) {
    if (e.key === 'Down') {
      channelDown();
      return false;
    }
    if (e.key === 'Up') {
      channelUp();
      return false;
    }
    if (e.which === 82) {
      $settingFlash.trigger('click');
    }
  });
}

buildChannelList();
handleHash();
handleKeyboard();
handleSettings();
handleFullscreen();
$(window).on('resize', handleFullscreen);

// Refresh list each minute
setInterval(function () {
  $.get('/api/channels.js', buildChannelList);
  $.get('/api/website.js');
}, 60000);

