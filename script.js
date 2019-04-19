(function () {

    const sidebar = document.getElementsByClassName('sidebar')[0];
    const body = document.getElementsByTagName('body')[0];
    const search = document.getElementById('search');
    const manifest = document.getElementsByClassName('manifest')[0];
    const aceId = document.getElementById('aceId');
    const channelContainer = document.getElementById('channelContainer');
    const bodyCoords = body.getBoundingClientRect();
    const ch = Array.prototype.slice.call(document.querySelectorAll('.sidebar .channellink')).map((o) => ({
        name: o.innerText,
        url: o.href
    }));

    function filterChannelList(list) {
        channelContainer.innerHTML = "";
        list.forEach((c, i) => {
            let li = document.createElement('li');
            let div = document.createElement('div');
            let a = document.createElement('a');
            div.className = 'channelRow';
            a.className = 'channelLink';
            a.href = c.url;
            a.innerText = c.name;
            a.setAttribute('tabindex', `${i + 2}`);
            div.appendChild(a);
            li.appendChild(div);
            channelContainer.appendChild(li);
        })
    }

    function findChannel(val) {
        if (val.length < 3) {
            filterChannelList(ch);
        } else {
            let list = [];
            ch.forEach((c) => {
                if (c.name.toLowerCase().indexOf(val.toLowerCase()) !== -1) {
                    list.push(c);
                }
            });
            filterChannelList(list);
        }
    }

    function showSidebar() {
        sidebar.style.right = '0px';
        search.focus();
        search.value = '';
    }

    function hideSideBar() {
        sidebar.style.right = '-250px';
        search.blur();
        search.value = '';
        aceId.blur();
        aceId.value = '';
    }

    body.addEventListener("mousemove", function (e) {
        if (bodyCoords.right - e.clientX < 30) {
            showSidebar();
        }
    });

    sidebar.addEventListener("mouseleave", function () {
        hideSideBar();
    });
    aceId.addEventListener("keyup", function (e) {
        if (e.key === 'Enter') {
            hideSideBar();
        }
    });

    search.addEventListener("keyup", function (e) {
        if (e.key === 'Enter') {
            hideSideBar();
        }
        findChannel(e.target.value);
    });

    window.addEventListener('keydown', function (e) {
        if (e.altKey && e.key === 'ArrowRight') {
            hideSideBar();
        } else if (e.altKey && e.key === 'ArrowLeft') {
            showSidebar();
        }
    });

    const video = document.getElementById('video');
    if (Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource('{{ play_link }}');
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function () {
            video.play();
        });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = '{{ play_link }}';
        video.addEventListener('loadedmetadata', function () {
            video.play();
        });
    }

    function copy(e) {
        const tempElem = document.createElement('input');
        body.appendChild(tempElem);
        tempElem.value = e.target.getAttribute('data-clipboard-text');
        tempElem.select();
        document.execCommand('copy');
        tempElem.remove();
    }

    manifest.addEventListener('click', e => {
        copy(e);
    });
})();
