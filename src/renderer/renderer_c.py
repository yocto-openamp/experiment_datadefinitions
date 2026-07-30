from pydantic import BaseModel


class RendererC:
    """Render a simple C struct definition from a Pydantic model."""

    _TYPE_MAP = {
        str: "char {name}[65];",
        int: "uint32_t {name};",
        float: "double {name};",
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

            json_schema_extra = field_info.json_schema_extra or {}
            comment = self._render_comment(field_name=field_name, extra=json_schema_extra)
            if comment:
                lines.append(f"    // {comment}")

            c_decl = self._TYPE_MAP[annotation].format(name=field_name)
            lines.append(f"    {c_decl}")

        struct_name = type(self.model).__name__
        lines.extend([f"}} {struct_name}_t;", ""])
        return "\n".join(lines)

    @staticmethod
    def _render_comment(field_name: str, extra: dict) -> str:
        comment = extra.get("Comment", "")
        unit = extra.get("Unit", "")

        if field_name == "value":
            if "4096 steps = 1 revolution" in unit:
                comment = "4096 steps per revolution"

        if unit:
            return f"[{unit}] {comment}".rstrip()

        return comment
