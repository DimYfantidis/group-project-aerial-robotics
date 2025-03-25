import time

def get_absolute_time_millis():
    """Return the current time in milliseconds."""
    return int(round(time.time() * 1000))

class PID:
    def __init__(self, p, i, d):
        # PID state variables.
        self.feedback = 0.0
        self.last_error = 0.0
        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0
        self.i_sum = 0.0

        # PID gains.
        self.p_gain = p
        self.i_gain = i
        self.d_gain = d

        # Time reference in milliseconds.
        self.ms_last_t = get_absolute_time_millis()
    
    def reset(self):
        """Reset PID controller state."""
        self.p_term = 0.0
        self.i_term = 0.0
        self.d_term = 0.0
        self.i_sum = 0.0
        self.last_error = 0.0
        self.feedback = 0.0
        self.ms_last_t = get_absolute_time_millis()
    
    def update(self, demand, measurement):
        """
        Update the PID controller.
        
        Parameters:
            demand (float): The setpoint value.
            measurement (float): The measured value.
        
        Returns:
            float: The PID feedback.
        """
        ms_now_t = get_absolute_time_millis()
        ms_dt = ms_now_t - self.ms_last_t
        
        # Update the timestamp for the next cycle.
        self.ms_last_t = get_absolute_time_millis()
        float_dt = float(ms_dt)
        
        # Protect against division by zero if update is called too quickly.
        if float_dt == 0.0:
            return self.feedback
        
        # Calculate error signal.
        error = demand - measurement

        # Compute derivative using the difference between current error and the last error.
        # (Note: It's important to compute the derivative before updating last_error.)
        diff_error = (error - self.last_error) / float_dt

        # Update last_error for the next update cycle.
        self.last_error = error

        # Proportional term.
        self.p_term = self.p_gain * error

        # Integral term (discrete integration).
        self.i_sum += error * float_dt
        self.i_term = self.i_gain * self.i_sum

        # Derivative term.
        self.d_term = self.d_gain * diff_error

        # Calculate total PID feedback.
        self.feedback = self.p_term + self.i_term + self.d_term
        return self.feedback


# Example usage:
if __name__ == "__main__":
    pid = PID(p=1.0, i=0.1, d=0.05)
    demand = 10.0         # Setpoint
    measurement = 0.0     # Initial measurement

    print("Starting PID control simulation...")
    for _ in range(10):
        output = pid.update(demand, measurement)
        print(f"Feedback: {output}")
        # For demonstration, simulate the process by adjusting the measurement.
        measurement += output * 0.1
        time.sleep(0.1)
