import numpy as np
from tensorflow.keras.layers import Input, LSTM, Dense, Concatenate
from tensorflow.keras.models import Model

def train_model(X_train_dyn, X_train_static, y_train, dynamic_shape, static_shape=None):
    #Train an LSTM and DNN hybrid model, handling static data flexibly.
    
    # Adjust static data to ensure all elements have the same size
    X_train_static_adjusted = []
    for static in X_train_static:
        if len(static) != static_shape:
            print(f"Adjusting static data size from {len(static)} to {static_shape}")
            # Pad static data to match static_shape
            static = static + [0] * (static_shape - len(static))
        X_train_static_adjusted.append(static)
    
    X_train_static_adjusted = np.array(X_train_static_adjusted, dtype=np.float32)

    # Dynamic data
    X_train_dyn = np.array(X_train_dyn).reshape(len(X_train_dyn), dynamic_shape[0], 1)

    # Define model
    dynamic_input = Input(shape=(dynamic_shape[0], dynamic_shape[1]), name='dynamic_input')
    static_input = Input(shape=(static_shape,), name='static_input')

    lstm_out = LSTM(64)(dynamic_input)
    dense_out = Dense(32, activation='relu')(static_input)

    concatenated = Concatenate()([lstm_out, dense_out])
    output = Dense(1, activation='sigmoid')(concatenated)

    model = Model(inputs=[dynamic_input, static_input], outputs=output)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit([X_train_dyn, X_train_static_adjusted], y_train, epochs=10, batch_size=32)

    return model

def predict_file(new_report, model, dynamic_shape, static_shape=None):
    #Predict if a file is malicious based on its report, with flexible handling of static data.
    from dynamic_analysis import extract_dynamic_features, analyze_behaviors
    from static_analysis import prepare_static_data
    
    # Prepare inputs for prediction
    dynamic_data = extract_dynamic_features(new_report).reshape(1, dynamic_shape[0], 1)
    static_data, static_analysis = prepare_static_data(new_report)

    # Handle static data adjustment for prediction
    if len(static_data) != static_shape:
        print(f"Warning: static_data for this report does not match expected shape {static_shape}. Adjusting...")
        static_data = static_data + [0] * (static_shape - len(static_data))

    static_data_array = np.array(static_data, dtype=np.float32).reshape(1, -1)
    
    try:
        prediction = model.predict([dynamic_data, static_data_array])
    except ValueError as e:
        print(f"Prediction error: {e}")
        prediction = [[0]]  # If error occurs, return Clean by default

    is_malicious = prediction[0][0] >= 0.5

    # Analyze behaviors
    behaviors = analyze_behaviors(new_report)

    # Return readable result
    return {
        'prediction': 'Malicious' if is_malicious else 'Clean',
        'behaviors': behaviors,
        'static_analysis': static_analysis
    }
    
# from tensorflow.keras.layers import Input, LSTM, Dense, Concatenate
# from tensorflow.keras.models import Model
# import numpy as np

# def train_model(X_train_dyn, X_train_static, y_train, dynamic_shape, static_shape):
#     """Train an LSTM and DNN hybrid model using Functional API to handle multiple inputs."""
    
#     # Define input for dynamic data
#     dynamic_input = Input(shape=(dynamic_shape[0], dynamic_shape[1]), name='dynamic_input')
    
#     # Define input for static data
#     static_input = Input(shape=(static_shape,), name='static_input')
    
#     # Define LSTM for dynamic data
#     lstm_out = LSTM(64)(dynamic_input)
    
#     # Define Dense layer for static data
#     dense_out = Dense(32, activation='relu')(static_input)
    
#     # Concatenate LSTM output with Dense layer output
#     concatenated = Concatenate()([lstm_out, dense_out])
    
#     # Output layer
#     output = Dense(1, activation='sigmoid')(concatenated)
    
#     # Create the model
#     model = Model(inputs=[dynamic_input, static_input], outputs=output)
    
#     # Compile the model
#     model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
#     # Train the model
#     model.fit([X_train_dyn, X_train_static], y_train, epochs=10, batch_size=32)
    
#     return model

# def predict_file(new_report, model, dynamic_shape, static_shape=None):
#     """Predict if a file is malicious based on its report, with flexible handling of static data."""
#     from dynamic_analysis import extract_dynamic_features, analyze_behaviors
#     from static_analysis import prepare_static_data
    
#     # Prepare inputs for prediction
#     dynamic_data = extract_dynamic_features(new_report).reshape(1, dynamic_shape[0], 1)
#     static_data, static_analysis = prepare_static_data(new_report)

#     # Handle static data adjustment for prediction
#     if len(static_data) != static_shape:
#         print(f"Warning: static_data for this report does not match expected shape {static_shape}. Adjusting...")
#         static_data = static_data + [0] * (static_shape - len(static_data))

#     static_data_array = np.array(static_data, dtype=np.float32).reshape(1, -1)
    
#     try:
#         prediction = model.predict([dynamic_data, static_data_array])
#     except ValueError as e:
#         print(f"Prediction error: {e}")
#         prediction = [[0]]  # If error occurs, return Clean by default

#     is_malicious = prediction[0][0] >= 0.2

#     # Analyze behaviors
#     behaviors = analyze_behaviors(new_report)

#     # Return readable result
#     return {
#         'prediction': 'Malicious' if is_malicious else 'Clean',
#         'behaviors': behaviors,
#         'static_analysis': static_analysis
#     }
