document.addEventListener('DOMContentLoaded', function() {
    // Các checkbox của danh sách phòng đã đặt
    const selectAllBookedRooms = document.getElementById('selectAllBookedRooms');
    const bookedRoomCheckboxes = document.querySelectorAll('#bookedRoomsTable tbody tr td input[type="checkbox"]');

    // Hiển thị tổng tiền
    const totalAmountDisplay = document.getElementById('totalAmount');

    // Hàm để chọn hoặc bỏ chọn tất cả checkbox
    function toggleCheckboxes(checkboxes, isChecked) {
        checkboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
        });
        calculateTotal(); // Cập nhật tổng tiền sau khi thay đổi checkbox
    }

    // Hàm tính tổng tiền
    function calculateTotal() {
        let total = 0;
        bookedRoomCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const row = checkbox.closest('tr');
                const price = parseInt(row.dataset.price || '0', 10);
                total += price;
            }
        });
        totalAmountDisplay.textContent = total.toLocaleString('vi-VN', { style: 'currency', currency: 'VND' });
    }

    // Hàm lấy danh sách các phòng đã chọn
    function getSelectedRooms() {
        const selectedRooms = [];
        bookedRoomCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const roomId = checkbox.getAttribute('data-room-id');
                console.log('Selected room ID:', roomId);  // Debugging line
                selectedRooms.push({ room_id: roomId });
            }
        });
        return selectedRooms;
    }



    // Hàm gửi yêu cầu lên server
    function sendRequest(url, data) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }).then(response => response.json());
    }

    // Sự kiện chọn tất cả cho danh sách phòng đã đặt
    selectAllBookedRooms.addEventListener('change', function() {
        toggleCheckboxes(bookedRoomCheckboxes, this.checked);
    });

    // Gán sự kiện cho mỗi checkbox trong danh sách phòng đã đặt
    bookedRoomCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (!this.checked) {
                selectAllBookedRooms.checked = false;
            }
            calculateTotal();
        });
    });

    // Sự kiện Xoá
    document.querySelector('.btn-delete').addEventListener('click', function() {
        console.log('Nút Xoá đã được nhấn');
        const selectedRooms = getSelectedRooms();

        if (selectedRooms.length > 0) {
            console.log('Phòng đã chọn:', JSON.stringify(selectedRooms, null, 2));
            sendRequest('/delete-selected-rooms', { rooms: selectedRooms })
                .then(data => {
                    if (data.status === 'success') {
                        alert('Phòng đã được xóa thành công!');
                        if (data.reload) {
                            location.reload();
                        }
                    } else {
                        alert('Có lỗi xảy ra: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Lỗi kết nối, vui lòng thử lại!');
                });
        } else {
            console.log('Không có phòng nào được chọn để xoá');
        }
    });

    // Sự kiện Thanh toán
    document.querySelector('.btn-pay').addEventListener('click', function() {
        console.log('Nút Thanh toán đã được nhấn');
        const selectedRooms = getSelectedRooms();
        const stripe = Stripe('pk_test_51QXAxiFyHL0Twlggl7sNXjDnaxX3RYY9XLJEvGaknQ6wPNuyMIMeZ20XpIbc4HhzDTkG5f9GDhEbdmvkRh2ifC8300x6aTawDW');
        if (selectedRooms.length > 0) {
            console.log('Phòng đã chọn:', selectedRooms);
            fetch('/create-checkout-session', {
                method: 'POST',
            headers: {
        'Content-Type': 'application/json',
        },
    body: JSON.stringify({ rooms: selectedRooms }), // Danh sách phòng được chọn
})
    .then((response) => response.json())
    .then((data) => {
        if (data.error) {
            console.error('Error creating checkout session:', data.error);
        } else {
            const sessionId = data.sessionId;
            return stripe.redirectToCheckout({ sessionId: sessionId });
        }
    })
    .catch((error) => console.error('Error:', error));

        }
    });

    // Tính tổng tiền ngay khi trang tải lần đầu
    calculateTotal();
});
