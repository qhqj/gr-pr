//控制联系人区域手动调整高度的大小。

document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    let startX = 0;
    let startWidth = 0;

    const onMouseDown = (event) => {
        startX = event.pageX;
        startWidth = parseInt(document.defaultView.getComputedStyle(sidebar).width, 10);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    };

    const onMouseMove = (event) => {
        const width = startWidth + (event.pageX - startX);
        // 添加条件来限制最小宽度
        if (width > 100) {
            sidebar.style.width = `${width}px`;
        }
    };

    const onMouseUp = () => {
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
    };

    sidebar.addEventListener('mousedown', onMouseDown);
});
