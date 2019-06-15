(function () {

    const sidebar = document.getElementsByClassName('sidebar')[0];
    const body = document.getElementsByTagName('body')[0];
    const search = document.getElementById('search');
    const manifest = document.getElementsByClassName('manifest')[0];
    const channelContainer = document.getElementById('channelContainer');
    const bodyCoords = body.getBoundingClientRect();
    const playLink = document.getElementById('playLink').innerText;
    const ch = Array.prototype.slice.call(document.querySelectorAll('.sidebar .channelLink')).map((o) => ({
        name: o.innerText,
        url: o.href
    }));

    function filterChannelList(list) {
        channelContainer.innerHTML = '';
        list.forEach((c, i) => {
            let li = document.createElement('li');
            if (manifest.innerText == c.name) {
                li.className = 'active';
            }
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
        let list = [];
        ch.forEach((c) => {
            if (c.name.toLowerCase().indexOf(val.toLowerCase()) !== -1) {
                list.push(c);
            }
        });
        filterChannelList(list);
    }

    function showSidebar() {
        if (sidebar.style.right != '0px') {
            sidebar.style.right = '0px';
            filterChannelList(ch);
            search.value = '';
            search.focus();
        }
    }

    function hideSideBar() {
        sidebar.style.right = '-250px';
        search.blur();
    }

    body.addEventListener("mousemove", function (e) {
        if (bodyCoords.right - e.clientX < 30) {
            showSidebar();
        }
    });

    sidebar.addEventListener("mouseleave", function () {
        hideSideBar();
    });
    sidebar.addEventListener('scroll', (e) => e.stopPropagation());

    search.addEventListener("input", function (e) {
        findChannel(e.target.value);
    });

    window.addEventListener('keydown', function (e) {
        if (e.altKey && e.key === 'ArrowRight') {
            hideSideBar();
        } else if (e.altKey && e.key === 'ArrowLeft') {
            showSidebar();
        }
    });
    let timer;
    const handleTouchStart = (e) => {
        const touchEndX = e.changedTouches[0].clientX;
        const touchEndY = e.changedTouches[0].clientY;
        const tapX = touchEndX / window.innerWidth;
        const tapY = touchEndY / window.innerHeight;
        if (tapX > 0.9 && tapY > 0.3 && tapY < 0.7) {
            timer = setTimeout(() => showSidebar(), 1000);
        } else if (tapX < 0.1 && tapY > 0.3 && tapY < 0.7) {
            hideSideBar();
        }
    };

    const handleTouchEnd = (e) => {
        clearTimeout(timer)
    };

    body.addEventListener("touchstart", handleTouchStart, false);
    body.addEventListener("touchend", handleTouchEnd, false);

    const video = document.getElementById('video');
    if (Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource(playLink);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function () {
            video.play();
        });
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = playLink;
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
