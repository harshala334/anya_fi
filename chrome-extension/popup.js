document.addEventListener('DOMContentLoaded', function () {
    const userIdInput = document.getElementById('userId');
    const saveBtn = document.getElementById('saveBtn');
    const statusDiv = document.getElementById('status');

    // Load saved ID
    chrome.storage.local.get(['telegram_user_id'], function (result) {
        if (result.telegram_user_id) {
            userIdInput.value = result.telegram_user_id;
        }
    });

    // Save ID
    saveBtn.addEventListener('click', function () {
        const userId = userIdInput.value.trim();
        if (userId) {
            chrome.storage.local.set({ telegram_user_id: userId }, function () {
                statusDiv.textContent = 'Saved! You are now protected.';
                setTimeout(() => { statusDiv.textContent = ''; }, 2000);
            });
        }
    });
});
