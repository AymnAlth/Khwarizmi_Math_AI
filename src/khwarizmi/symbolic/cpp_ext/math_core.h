#ifndef KHWARIZMI_MATH_CORE_H
#define KHWARIZMI_MATH_CORE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32) || defined(__CYGWIN__)
  #ifdef BUILDING_MATH_CORE
    #define MATH_CORE_API __declspec(dllexport)
  #else
    #define MATH_CORE_API __declspec(dllimport)
  #endif
#else
  #define MATH_CORE_API __attribute__((visibility("default")))
#endif

/**
 * Validates LaTeX brackets, braces, and environment balance.
 * Returns 1 if balanced and valid, 0 if syntax error detected.
 */
MATH_CORE_API int32_t khwarizmi_validate_latex_brackets(const char* latex_str);

/**
 * Normalizes LaTeX spacing, operators, and basic fraction notations.
 * Output buffer must be allocated by caller.
 * Returns length of normalized string, or -1 on error.
 */
MATH_CORE_API int32_t khwarizmi_normalize_latex(const char* input_str, char* output_buf, int32_t max_out_len);

/**
 * Fast 64-bit canonical FNV-1a hash for formula deduplication.
 */
MATH_CORE_API uint64_t khwarizmi_formula_hash(const char* latex_str);

#ifdef __cplusplus
}
#endif

#endif // KHWARIZMI_MATH_CORE_H
