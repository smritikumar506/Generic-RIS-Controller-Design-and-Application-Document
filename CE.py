from flask import Flask, jsonify
import time
import logging
from gnuradio import blocks
from gnuradio import gr
from gnuradio import uhd
from threading import Thread

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class cos_rx(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "Signal Receiver")
        self.samp_rate = 32000  # Sample rate
        # self.samp_rate = 64000  # Sample rate

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("",'')), #"addr=192.168.10.2",  # or "type=b200"
            uhd.stream_args(
                cpu_format="fc32",
                channels=list(range(0, 1)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_center_freq(3500000000, 0)  # Set frequency
        self.uhd_usrp_source_0.set_gain(100, 0)  # Set gain

        # Blocks for processing
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_probe_signal_x_0 = blocks.probe_signal_f()

        # Connect blocks
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_probe_signal_x_0, 0))

        # Initialize buffer for averaging
        self.magnitude_buffer = []
        # self.average_window = 20  # We will average every 20 samples
    
    # def get_current_magnitude(self):
    #     """Get the current magnitude from the probe."""
    #     magnitude = self.blocks_probe_signal_x_0.level()
    #     logging.debug("Current magnitude: %s", magnitude)
    #     return magnitude

    def get_current_magnitude(self):
        """Get the current magnitude from the probe and average every 20 samples."""
        magnitude = self.blocks_probe_signal_x_0.level()
        logging.debug("Current magnitude: %s", magnitude)
        # print(magnitude)
        return magnitude
        # Add magnitude to buffer
        # self.magnitude_buffer.append(magnitude)
        # print('*******')
        # print(len(self.magnitude_buffer))
        # print('*******')

    #    # Check if we have enough samples to average
    #     if len(self.magnitude_buffer) >= self.average_window:
    #        avg_magnitude = sum(self.magnitude_buffer) / self.average_window
    #        self.magnitude_buffer.clear()  # Reset buffer after averaging
    #        logging.debug("Averaged magnitude: %s", avg_magnitude)
           
    #        return avg_magnitude
    #     else:
    #        return magnitude  # Return None if not enough samples to average yet
        # avg_magnitude = sum(self.magnitude_buffer) / len(self.magnitude_buffer)
        # return avg_magnitude


@app.route('/api/v1/magnitude', methods=['GET'])
def get_magnitude():
    magnitude = flowgraph.get_current_magnitude()
    # time.sleep(2)
    #print(magnitude)
    return jsonify({'magnitude': magnitude})

def main(top_block_cls=cos_rx):
    global flowgraph
    flowgraph = top_block_cls()

    flowgraph.start()

    # Start the Flask server in a separate thread
    def run_flask():
        try:
            app.run(host='0.0.0.0', port=5000, threaded=True)
        except Exception as e:
            logging.error("Flask server stopped due to an error: %s", e)

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Keep running until stopped
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        pass

    flowgraph.stop()
    flowgraph.wait()

if __name__ == '__main__':  # Corrected entry point
    main()
