#include "dump_values.hpp"

#include "generated_pid_controller_struct.hpp"
#include "generated_system_dual_struct.hpp"

#include "generated_pid_controller_initializer.hpp"
#include "generated_system_dual_initializer.hpp"

int main()
{
	dump_struct(system_dual);

	/*
	Print out some variables.
	Note: Code completion.
	Note: Help text when hovering.
	Note: Failures when variable names change.
	*/
	std::fprintf(stderr, "axis_x.name='%s', axis_y.name='%s', debuglevel=%d\n", system_dual.axis_x.name, system_dual.axis_y.name, system_dual.debuglevel);

	return 0;
}
