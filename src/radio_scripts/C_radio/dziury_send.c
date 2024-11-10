#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <windows.h>

int send_data(HANDLE serial_handle, const char *data) {
    DWORD bytes_written;
    if (!WriteFile(serial_handle, data, 36, &bytes_written, NULL)) {
        printf("Error writing to serial port\n");
        return -1;
    }
    return bytes_written;
}

HANDLE open_serial(const char *port, int baud_rate) {
    HANDLE serial_handle = CreateFile(port, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL);
    if (serial_handle == INVALID_HANDLE_VALUE) {
        printf("Failed to open serial port\n");
        return NULL;
    }

    DCB dcb_serial_params = {0};
    dcb_serial_params.DCBlength = sizeof(dcb_serial_params);

    if (!GetCommState(serial_handle, &dcb_serial_params)) {
        printf("Error getting state\n");
        CloseHandle(serial_handle);
        return NULL;
    }

    dcb_serial_params.BaudRate = baud_rate;
    dcb_serial_params.ByteSize = 8;
    dcb_serial_params.StopBits = ONESTOPBIT;
    dcb_serial_params.Parity = NOPARITY;

    if (!SetCommState(serial_handle, &dcb_serial_params)) {
        printf("Error setting serial port state\n");
        CloseHandle(serial_handle);
        return NULL;
    }

    COMMTIMEOUTS timeouts = {0};
    timeouts.ReadIntervalTimeout = 50;
    timeouts.ReadTotalTimeoutConstant = 50;
    timeouts.ReadTotalTimeoutMultiplier = 10;
    timeouts.WriteTotalTimeoutConstant = 50;
    timeouts.WriteTotalTimeoutMultiplier = 10;

    SetCommTimeouts(serial_handle, &timeouts);

    return serial_handle;
}

void main_loop(HANDLE serial_handle, int sending_frequency) {
    int freqs[7] = {800,1600,3200,6400,12800};
    for (int j=1; j<7;j++)
    {
        int i = 1;
        int delay = 1000 / (freqs[j]); // in milliseconds
        clock_t start = clock();

        while ((clock() - start) < 10 * CLOCKS_PER_SEC) {
            clock_t now = clock();
            long time_ms = (long)((now * 1000) / CLOCKS_PER_SEC);

            char data_to_send[37]; // 36 bytes + 1 for null terminator
            int checksum = i + time_ms;

            // Format the message to exactly 36 bytes, padding/truncating as necessary
            snprintf(data_to_send, sizeof(data_to_send), "G%05d%013ld%08dS%07d", i, time_ms, checksum, 0);

            int n = send_data(serial_handle, data_to_send);
            if (i%30 == 0)
            {
                printf("%d Sent %d bytes: %s\n",i, n, data_to_send);
            }

            i++;
            Sleep(delay); // sleep for delay milliseconds
        }
        float speed = 36*i/10;
        printf("Sent: %d Freq: %d, Speed = %f\n", i,freqs[j], speed);
    }
}

int main(int argc, char *argv[]) {
    const char *selected_port = "COM5";
    int detected_baud = CBR_115200;
    int sending_frequency = 50;

    if (argc > 1) {
        selected_port = argv[1];
        sending_frequency = atoi(argv[2]);
    }

    HANDLE serial_handle = open_serial(selected_port, detected_baud);
    if (serial_handle == NULL) {
        return 1;
    }

    main_loop(serial_handle, sending_frequency);

    CloseHandle(serial_handle);
    return 0;
}