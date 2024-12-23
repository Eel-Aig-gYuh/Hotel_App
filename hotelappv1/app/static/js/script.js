const bookedRoomCheckboxes = document.querySelectorAll('#bookedRoomsTable tbody tr td input[type="checkbox"]');

function addToCart(room_id, room_name, room_type_name, room_type_price_per_night, room_type_capacity, checkin_date, checkout_date) {
    // Get the cart from sessionStorage
    let cart = JSON.parse(sessionStorage.getItem('cart')) || {};

    // Check if the room is already in the cart
    if (cart[room_id]) {
        alert('Phòng đã có trong giỏ hàng!');
        console.info(cart)

        return; // Exit without adding the room again
    }

    // Add the room to the cart
    const newRoom = {
        room_id: room_id,
        room_name: room_name,
        room_type_name: room_type_name,
        room_type_price_per_night: room_type_price_per_night,
        room_type_capacity: room_type_capacity,
        checkin_date: checkin_date,
        checkout_date: checkout_date,
        is_foreign: 1,
        quantity: 1,
    };

    // Save the new room to the cart in sessionStorage
    cart[room_id] = newRoom;
    sessionStorage.setItem('cart', JSON.stringify(cart));

    fetch('/api/carts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "room_id": room_id,
            "room_name": room_name,
            "room_type_name": room_type_name,
            "room_type_price_per_night": room_type_price_per_night,
            "room_type_capacity": room_type_capacity,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "is_foreign": 1,
            "quantity": 1
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.info(data)
        updateUI(data)
        alert('Thêm phòng vào giỏ hàng thành công!');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Đã xảy ra lỗi, vui lòng thử lại.');
    });
}

function updateCart(room_id, obj) {
    fetch(`/api/carts/${room_id}`, {
        method: "put",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify ({

        })
    }).then(res => res.json()).then(data => {
        updateUI(data)
    })
}

function cancelBook(booking_id) {
    if (confirm("Bạn có chắc muốn hủy phòng không?") === true) {
        fetch(`/api/carts/${booking_id}`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) {
                alert(data.msg || "Hủy phòng thành công!");
                location.reload();
            } else {
                alert(data.err_msg || "Không thể hủy phòng!");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Đã xảy ra lỗi khi hủy phòng!");
        });
    }
}

function checkInRoom(booking_id) {
    if (confirm("Khách hàng đã nhận phòng này?") === true) {
        fetch(`/api/carts/checkin/${booking_id}`, {
            method: "PUT",
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) {
                alert(data.msg || "Nhận phòng thành công!");
                location.reload();
            } else {
                alert(data.err_msg || "Không thể nhận phòng!");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Đã xảy ra lỗi khi nhận phòng!");
        });
    }
}

function deleteCart(room_id) {
    if (confirm("Bạn có chắc chắn muốn xóa không?") === true){
        fetch(`/api/carts/${room_id}`, {
            method: "delete"
        }).then(res => res.json()).then(data => {
            deleteCartItem(room_id)
            updateUI(data);
            document.getElementById(`cart${room_id}`).style.display="none";
        })
    }
}

function deleteCartItem(item_id) {
    // Retrieve the cart from sessionStorage
    let cart = JSON.parse(sessionStorage.getItem('cart'));

    // Check if cart exists and the item_id is in the cart
    if (cart && cart.hasOwnProperty(item_id)) {
        // Delete the item with the given item_id
        delete cart[item_id];

        // Optionally, remove the item from the UI if it's displayed
        const cartItemElement = document.getElementById(`cart${item_id}`);
        if (cartItemElement) {
            cartItemElement.style.display = "none";  // Hide the cart item element
        }

        // Save the updated cart back to sessionStorage
        sessionStorage.setItem('cart', JSON.stringify(cart));

        console.log(`Đã xóa thành công phòng ${item_id} ra khỏi cart.`);
    } else {
        console.log(`${item_id} không tìm thấy trong cart.`);
    }
}


function setDefaultDates(checkinId, checkoutId) {
    const today = new Date().toISOString().split('T')[0];
    const tomorrow = new Date(new Date().setDate(new Date().getDate() + 1)).toISOString().split('T')[0];

    const checkinField = document.getElementById(checkinId);
    const checkoutField = document.getElementById(checkoutId);

    if (checkinField) {
        checkinField.value = today;
        checkinField.setAttribute('min', today);
    }

    if (checkoutField) {
        checkoutField.value = tomorrow;
        checkoutField.setAttribute('min', today);
    }
}

function updateUI(data){
    let counters = document.getElementsByClassName("cart-counter");
    for (let c of counters)
        c.innerText = data.total_quantity;
}

async function pay() {
    const selectedRooms = Array.from(document.querySelectorAll('.room-checkbox:checked')).map(checkbox =>
        checkbox.getAttribute('data-room-id')
    );

    if (selectedRooms.length === 0) {
        alert('Vui lòng chọn ít nhất một phòng để thanh toán.');
        return;
    }

    if (confirm("Bạn có chắc chắn muốn thanh toán không?") === true) {
        try {
            const response = await fetch("/api/pay", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ selected_room_ids: selectedRooms }), // Pass the selected rooms here
            });

            const data = await response.json();

            if (data.status === 200) {
                alert(data.msg || "Thanh toán thành công!");

                // Update UI or session storage
                selectedRooms.forEach(roomId => {
                    const cartItemElement = document.getElementById(`cart${roomId}`);
                    if (cartItemElement) {
                        cartItemElement.style.display = "none"; // Hide the cart item element
                    }
                });

                // Optionally clear the cart for those rooms
                sessionStorage.removeItem('cart'); // Adjust if you manage cart differently

                console.log("Thanh toán thành công:", selectedRooms);
                location.reload();
            } else {
                alert(data.err_msg || "Thanh toán không thành công!");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Đã xảy ra lỗi khi thanh toán.");
        }
    }
}

function addComment(room_id, room_name, room_style, room_price, room_capacity, checkin, checkout, room_type_id){
    fetch(`/rooms/room_detail/${room_id}/${room_name}/${room_style}/${room_price}/${room_capacity}/${checkin}/${checkout}/comments`, {
        method: 'post',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "content": document.getElementById("content").value
        })
    }).then(res => res.json()).then(c => {
        location.reload()
    })
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

    // Sự kiện Thanh toán
   document.querySelector('.btn-pay').addEventListener('click', function () {
    console.log('Nút Thanh toán đã được nhấn');

    const selectedRooms = Array.from(document.querySelectorAll('.room-checkbox:checked')).map(checkbox =>
        checkbox.getAttribute('data-room-id')
    );

    if (selectedRooms.length === 0) {
        alert('Vui lòng chọn ít nhất một phòng để thanh toán.');
        return;
    }

    fetch('/create-checkout-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rooms: selectedRooms }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.sessionId) {
                const stripe = Stripe('pk_test_51QXAxiFyHL0Twlggl7sNXjDnaxX3RYY9XLJEvGaknQ6wPNuyMIMeZ20XpIbc4HhzDTkG5f9GDhEbdmvkRh2ifC8300x6aTawDW'); // Replace with your actual publishable key
                return stripe.redirectToCheckout({ sessionId: data.sessionId });
            } else {
                alert('Không thể tạo phiên thanh toán.');
            }
        })
        .then(result => {
            if (result && result.error) {
                console.error('Error:', result.error.message);
                alert('Đã xảy ra lỗi khi chuyển đến trang thanh toán.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Có lỗi xảy ra trong quá trình thanh toán.');
        });
});

    // Tính tổng tiền ngay khi trang tải lần đầu
    calculateTotal();
});
