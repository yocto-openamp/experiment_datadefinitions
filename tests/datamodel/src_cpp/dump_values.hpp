#pragma once

#include <cstddef>
#include <cstdint>
#include <cstdio>

inline void bytes_to_hex(const void *data, std::size_t len, char *out)
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

/*
Dump structure as binary blob
*/
template <typename T>
void dump_struct(const T &value)
{
	char hexbuf[4096];
	bytes_to_hex(&value, sizeof(value), hexbuf);
	std::printf(">0x%s<\n", hexbuf);
}
