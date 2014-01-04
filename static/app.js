var $body = $('body'),
  channels = {},
  newChannelNames = [],
  $channels,
  $channelsSection = $('#channel-list'),
  $player = $('#player'),
  mode = 'channels',
  style = '',
  progName = location.href.toString().split('/')[6],
  $progLink,
  controlSocket;

// FUNCTIONS

function scrollChannelListToLink($progLink) {
  var $progItem = $progLink.parents('li').first(),
    scroll;

  scroll = $progItem.position().top - window.innerHeight / 2 + $progItem.height() / 2;
  $channels.scrollTop($channels.scrollTop() + scroll)

  $player.attr('src', $progLink.attr('href'));
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

function channelRefresh() {
  var $progLink = $channels.find('.current').find('a');
  $progLink.trigger('click');
}

function handleRemoteControl() {
  var controlSocket = new WebSocket("ws://localhost:1337/"),
    reconnectsLimit = 10;

  handleRemoteControl.reconnects = handleRemoteControl.reconnects || 0;

  controlSocket.onmessage = function (msg) {
    msg.data == 'CH_UP' && channelDown();
    msg.data == 'CH_DOWN' && channelUp();
    msg.data == 'REFRESH' && channelRefresh();
  };
  controlSocket.onerror = function () {
    handleRemoteControl.reconnects = reconnectsLimit;
    alert('No remote control support');
  };
  controlSocket.onclose = function () {
    handleRemoteControl.reconnects += 1;
    if (handleRemoteControl.reconnects < reconnectsLimit) {
      handleRemoteControl(); // retry
    } else {
      controlSocket.onerror();
    }
  };
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
      chHref = '/player/' + ch.cid + (ch.multibitrate === '1' ? '/hd.html' : '/sd.html'),
      $chLogo = $('<img alt="" class="logo"/>').attr('src', chLogo),
      $chThumb = $('<img alt="" class="thumb"/>').attr('src', chThumb),
      $chLink = $('<a target="player"/>').attr('id', 'link-' + chName).attr('href', chHref).on('click', function (ev) {
          var $this = $(this);
	  location.hash = $this.attr('id').replace('link-', '#play-');
          $channels.find('.current').removeClass('current');
          $this.parent().addClass('current');
          $player.show();
          $body.attr('class', 'both');
          scrollChannelListToLink($this);
          return !ev.skipLoad;
      }),
      $newCh = $('<li></li>');

    $newCh.append($chThumb);
    $newCh.append($chLogo);
    $newCh.wrapInner($chLink);

    $newChannels.append($newCh);
  }

  $newChannels.prepend($('<li id="go-to-grid"><a href="."><img src="/static/grid.png" alt="grid"></a></li>'));

  oldScrollTop = $channels && $channels.scrollTop();
  currentLink = $channels && $channels.find('.current a').attr('id')

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

buildChannelList();
handleHash();
handleRemoteControl();

// Refresh list each minute
setInterval(function () {
  $.get('/api/channels.js', buildChannelList);
}, 60000);
