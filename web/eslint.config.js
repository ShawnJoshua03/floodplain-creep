import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist", "node_modules", "src/api/generated"] },
  js.configs.recommended,
  ...tseslint.configs.strict,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: { globals: { ...globals.browser } },
    plugins: { "react-hooks": reactHooks },
    rules: {
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "error",
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-non-null-assertion": "error",
      "@typescript-eslint/ban-ts-comment": ["error", { "ts-ignore": true, "ts-expect-error": true, "ts-nocheck": true }],
      "@typescript-eslint/naming-convention": [
        "error",
        { selector: "default", format: ["camelCase"], leadingUnderscore: "forbid" },
        { selector: "variable", format: ["camelCase", "PascalCase", "UPPER_CASE"] },
        { selector: "function", format: ["camelCase", "PascalCase"] },
        { selector: "typeLike", format: ["PascalCase"] },
        { selector: "enumMember", format: ["UPPER_CASE", "PascalCase"] },
        { selector: ["property", "parameter"], format: null },
        { selector: "import", format: null },
      ],
      "no-restricted-globals": ["error", { name: "fetch", message: "Use web/src/api/client.ts." }],
      "no-restricted-syntax": [
        "error",
        { selector: "ClassDeclaration", message: "Use function components and hooks, no classes." },
        { selector: "ClassExpression", message: "Use function components and hooks, no classes." },
        { selector: "CallExpression[callee.property.name='then']", message: "Use async/await, not .then()." },
        { selector: "CallExpression[callee.property.name='catch']", message: "Use try/catch with async/await." },
      ],
    },
  },
  {
    files: ["src/api/**/*.{ts,tsx}"],
    rules: { "no-restricted-globals": "off" },
  },
  {
    files: ["eslint.config.js", "vite.config.ts"],
    languageOptions: { globals: { ...globals.node } },
    rules: { "@typescript-eslint/naming-convention": "off" },
  },
);
