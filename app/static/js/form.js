document.addEventListener('DOMContentLoaded', function () {
    const statusRadios = document.querySelectorAll('input[name="status"]');
    const needsLunchboxRadios = document.querySelectorAll('input[name="needs_lunchbox"]');
    const lunchboxGroup = document.getElementById('lunchbox-group');
    const dietGroup = document.getElementById('diet-group');

    // 輔助函式：動態顯隱與更新高度動畫
    function toggleField(element, show) {
        if (!element) return;
        if (show) {
            element.classList.add('show');
            element.style.maxHeight = element.scrollHeight + 'px';
        } else {
            element.classList.remove('show');
            element.style.maxHeight = '0px';
        }
    }

    // 當「出席意願」改變時
    function handleStatusChange() {
        const selectedStatus = document.querySelector('input[name="status"]:checked')?.value;
        if (selectedStatus === '是') {
            toggleField(lunchboxGroup, true);
            // 重新評估餐盒偏好的顯示
            handleLunchboxChange();
        } else {
            toggleField(lunchboxGroup, false);
            toggleField(dietGroup, false);
            
            // 重置未顯示欄位的值
            needsLunchboxRadios.forEach(radio => radio.checked = false);
            document.querySelectorAll('input[name="dietary_preference"]').forEach(radio => radio.checked = false);
        }
    }

    // 當「是否需要餐盒」改變時
    function handleLunchboxChange() {
        const selectedLunchbox = document.querySelector('input[name="needs_lunchbox"]:checked')?.value;
        const selectedStatus = document.querySelector('input[name="status"]:checked')?.value;

        if (selectedStatus === '是' && selectedLunchbox === '是') {
            toggleField(dietGroup, true);
        } else {
            toggleField(dietGroup, false);
            // 重置未顯示欄位的值
            document.querySelectorAll('input[name="dietary_preference"]').forEach(radio => radio.checked = false);
        }
    }

    // 綁定事件監聽器
    statusRadios.forEach(radio => {
        radio.addEventListener('change', handleStatusChange);
    });

    needsLunchboxRadios.forEach(radio => {
        radio.addEventListener('change', handleLunchboxChange);
    });

    // 初始化頁面時自動評估（用於處理表單驗證失敗重新載入時的狀態保留）
    handleStatusChange();
});
