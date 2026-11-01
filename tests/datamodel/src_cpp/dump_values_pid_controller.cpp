#include "dump_values.hpp"

#include "generated_pid_controller_struct.hpp"

#include "generated_pid_controller_initializer.hpp"

int main()
{
	dump_struct(pid_controller);

	/*
	Print out some variables.
	Note: Code completion.
	Note: Help text when hovering.
	Note: Failures when variable names change.
	*/
	std::fprintf(stderr, "name='%s', value=%d, i_param=%f\n", pid_controller.name, pid_controller.value, pid_controller.i_param);

	return 0;
}
