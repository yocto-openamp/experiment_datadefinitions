set -euox pipefail

g++ -Wall -Wextra dump_values_pid_controller.cpp -o generated_dump_values_pid_controller
g++ -Wall -Wextra dump_values_dual.cpp -o generated_dump_values_dual
