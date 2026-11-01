#include "dump_values.hpp"

#include "generated_pid_controller_struct.hpp"
#include "generated_system_list_struct.hpp"

#include "generated_pid_controller_initializer.hpp"
#include "generated_system_list_initializer.hpp"

int main()
{
	dump_struct(system_list);

	/*
	Print out some variables.
	Note: Code completion.
	Note: Help text when hovering.
	Note: Failures when variable names change.
	*/
	std::fprintf(stderr, "controllers[0].name='%s', controllers[1].name='%s', debuglevel=%d\n", system_list.controllers[0].name, system_list.controllers[1].name, system_list.debuglevel);

	return 0;
}
