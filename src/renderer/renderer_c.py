from pydantic import BaseModel


class RendererC:
    """Render a simple C struct definition from a Pydantic model."""

    _TYPE_MAP = {
        str: ("char {name}[65];      ", "// Up to 64 characters + null terminator"),
        int: ("uint32_t {name};     ", "// Unsigned 32-bit integer"),
        float: ("double {name};     ", "// Double-precision floating-point"),
    }

    def __init__(self, model: BaseModel) -> None:
        self.model = model

    def render_c_struct(self) -> str:
        """
        Render 'self.model' into something like:

            typedef struct
            {
                char name[65];      // Up to 64 characters + null terminator
                uint32_t value;     // Unsigned 32-bit integer
                double i_param;     // Double-precision floating-point
            } ModelPidController_t;
        """
        lines = ["", "typedef struct", "{"]

        for field_name, field_info in type(self.model).model_fields.items():
            annotation = field_info.annotation
            if annotation not in self._TYPE_MAP:
                raise ValueError(
                    f"Unsupported field type for '{field_name}': {annotation}"
                )

            c_decl, c_comment = self._TYPE_MAP[annotation]
            lines.append(f"    {c_decl.format(name=field_name)}{c_comment}")

        struct_name = type(self.model).__name__
        lines.extend([f"}} {struct_name}_t;", ""])
        return "\n".join(lines)
