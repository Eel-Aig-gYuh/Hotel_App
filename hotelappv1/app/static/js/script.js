//document.addEventListener('DOMContentLoaded', function() {
//    // Các checkbox của danh sách phòng đã đặt
//    const selectAllBookedRooms = document.getElementById('selectAllBookedRooms');
//    const bookedRoomCheckboxes = document.querySelectorAll('#bookedRoomsTable tbody tr td input[type="checkbox"]');
//
//    // Các checkbox của lịch sử thanh toán
//    const selectAllPaymentHistory = document.getElementById('selectAllPaymentHistory');
//    const paymentHistoryCheckboxes = document.querySelectorAll('#paymentHistoryTable tbody tr td input[type="checkbox"]');
//
//    // Hiển thị tổng tiền
//    const totalAmountDisplay = document.getElementById('totalAmount');
//
//    // Hàm để chọn hoặc bỏ chọn tất cả checkbox
//    function toggleCheckboxes(checkboxes, isChecked) {
//        checkboxes.forEach(checkbox => {
//            checkbox.checked = isChecked;
//        });
//        calculateTotal(); // Cập nhật tổng tiền sau khi thay đổi checkbox
//    }
//
//    // Hàm tính tổng tiền
//    function calculateTotal() {
//        let total = 0;
//        bookedRoomCheckboxes.forEach(checkbox => {
//            if (checkbox.checked) {
//                const row = checkbox.closest('tr');
//                const price = parseInt(row.dataset.price || '0', 10);
//                total += price;
//            }
//        });
//        totalAmountDisplay.textContent = total.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' });
//    }
//
//    // Sự kiện cho checkbox tiêu đề "Tích tất cả" của danh sách phòng đã đặt
//    selectAllBookedRooms.addEventListener('change', function() {
//        toggleCheckboxes(bookedRoomCheckboxes, this.checked);
//    });
//
//
//    // Gán sự kiện cho mỗi checkbox trong danh sách phòng đã đặt
//    bookedRoomCheckboxes.forEach(checkbox => {
//        checkbox.addEventListener('change', function() {
//            // Nếu bỏ chọn một phòng thì bỏ chọn "Tích tất cả"
//            if (!this.checked) {
//                selectAllBookedRooms.checked = false;
//            }
//            // Cập nhật tổng tiền
//            calculateTotal();
//        });
//    });
//
//    // Gán sự kiện cho mỗi checkbox trong lịch sử thanh toán (thực hiện tính tổng tiền khi tích tất cả)
//    paymentHistoryCheckboxes.forEach(checkbox => {
//        checkbox.addEventListener('change', function() {
//            // Nếu bỏ chọn một phòng thì bỏ chọn "Tích tất cả"
//            if (!this.checked) {
//                selectAllPaymentHistory.checked = false;
//            }
//            // Cập nhật tổng tiền
//            calculateTotal();
//        });
//    });
//
//    //Sự kiện Xoá
//    document.querySelector('.btn-delete').addEventListener('click', function() {
//    console.log('Nút Xoá đã được nhấn');
//    const selectedRooms = [];
//
//    bookedRoomCheckboxes.forEach(checkbox => {
//        if (checkbox.checked) {
//            const roomName = checkbox.getAttribute('data-room-name');
//            selectedRooms.push({ name: roomName });
//        }
//    });
//
//    // Gửi thông tin phòng đã chọn tới server
//    if (selectedRooms.length > 0) {
//        console.log('Phòng đã chọn:', selectedRooms);
//        fetch('/delete-selected-rooms', {
//            method: 'POST',
//            headers: {
//                'Content-Type': 'application/json',
//            },
//            body: JSON.stringify({ rooms: selectedRooms })
//        })
//        .then(response => response.json())
//        .then(data => {
//            if (data.status === 'success') {
//        alert('Phòng đã được xóa thành công!');
//        if (data.reload) {
//            location.reload();  // Tải lại trang pay
//        }
//    } else {
//        alert('Có lỗi xảy ra: ' + data.message);
//    }
//        })
//        .catch(error => {
//            console.error('Error:', error);
//        });
//    } else {
//        console.log('Không có phòng nào được chọn để xoá');
//    }
//});
//
//    // Tính tổng tiền ngay khi trang tải lần đầu (nếu cần)
//    calculateTotal();
//});

//document.querySelector('.form-select').addEventListener('change', function() {
//    const selectedValue = this.value;
//    // return selectedValue;
//});
