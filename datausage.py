@app.route('/use_data', methods=['POST'])
def use_data():
    if 'user_id' not in session:
        return jsonify({'message': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    if user.data_used >= 50.0:
        return jsonify({'message': 'Data limit reached'}), 403
    
    data_amount = request.get_json().get('data_amount', 0.0)
    user.data_used += data_amount
    db.session.commit()
    
    if user.data_used >= 50.0:
        return jsonify({'message': 'Data limit reached, please pay to continue'}), 403
    
    return jsonify({'message': f'{data_amount} MB used, total: {user.data_used} MB'}), 200
