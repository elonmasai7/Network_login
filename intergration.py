import random

@app.route('/pay', methods=['POST'])
def pay():
    if 'user_id' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    if user.data_used < 50.0:
        return jsonify({'message': 'No need to pay yet'}), 400
    
    # Simulate M-Pesa payment
    payment_success = random.choice([True, False])  # Randomly choose if the payment is successful
    
    if payment_success:
        user.data_used = 0.0
        user.paid = True
        db.session.commit()
        return jsonify({'message': 'Payment successful, data limit reset'}), 200
    else:
        return jsonify({'message': 'Payment failed, please try again'}), 500
