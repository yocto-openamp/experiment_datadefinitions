#include <cstddef>
#include <cstdint>
#include <cstdio>

#include "generated_pid_controller_struct.hpp"

#include "generated_pid_controller_initializer.hpp"

void bytes_to_hex(const void *data, std::size_t len, char *out)
{
	static const char hex[] = "0123456789ABCDEF";
	const auto *p = static_cast<const std::uint8_t *>(data);

	for (std::size_t i = 0; i < len; ++i)
	{
		out[2 * i] = hex[p[i] >> 4];
		out[2 * i + 1] = hex[p[i] & 0x0F];
	}
	out[2 * len] = '\0';
}

int main()
{
	/*
	Dump pid_controller structure as binary blob
	*/
	char hexbuf[4096];
	bytes_to_hex(&pid_controller, sizeof(pid_controller), hexbuf);
	std::printf(">0x%s<\n", hexbuf);

	/*
	Print out some variables.
	Note: Code completion.
	Note: Help text when hovering.
	Note: Failures when variable names change.
	*/
	std::fprintf(stderr, "name='%s', value=%d, i_param=%f\n", pid_controller.name, pid_controller.value, pid_controller.i_param);

	return 0;
}