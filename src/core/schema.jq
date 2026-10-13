def text: type == "string" and length > 0 and (test("[\u0000-\u001f\u007f]") | not);
def ident: type == "string" and test("^[A-Za-z0-9_-]+$");
def entry: type == "string" and test("^[A-Za-z0-9_-]+[.]sh$");
def integer_between($lo; $hi): type == "number" and floor == . and . >= $lo and . <= $hi;
def optional($key; rule): if has($key) then .[$key] | rule else true end;
def unique_ids: map(.id) as $ids | ($ids | length) == ($ids | unique | length);
type == "object" and (
  if $kind == "auth" then
    optional("enabled"; type == "boolean") and
    optional("case_sensitive"; type == "boolean") and
    optional("code_length"; integer_between(1; 64)) and
    optional("max_attempts"; integer_between(1; 100)) and
    optional("delay_on_failure"; integer_between(0; 60))
  elif $kind == "project" then
    all(.name, .version, .license, .language, .platform, .repository; text)
  elif $kind == "categories" then
    (.categories | type == "array" and unique_ids and
      all(.[]; type == "object" and (.id | ident) and (.name | text) and (.enabled | type == "boolean")))
  elif $kind == "functions" then
    (.functions | type == "array" and unique_ids and
      all(.[]; type == "object" and (.id | ident) and (.name | text) and
        (.entry | entry) and (.category | ident) and (.enabled | type == "boolean") and optional("library"; ident)))
  elif $kind == "metadata" then
    (.id | ident) and (.name | text) and (.version | text) and (.type | text) and
    (.category | ident) and (.entry | entry) and (.library | ident) and (.enabled | type == "boolean")
  elif $kind == "colors" then
    all(.reset, .bold, .dim, .black, .red, .green, .yellow, .blue, .magenta, .cyan,
        .white, .gray, .bright_red, .bright_green, .bright_yellow, .bright_blue,
        .bright_magenta, .bright_cyan, .bright_white;
        type == "string" and test("^\u001b\\[[0-9;]+m$"))
  else false end
)
