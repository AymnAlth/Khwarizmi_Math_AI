#include "math_core.h"
#include <string>
#include <vector>
#include <cstring>
#include <algorithm>
#include <cctype>

extern "C" {

int32_t khwarizmi_validate_latex_brackets(const char* latex_str) {
    if (!latex_str) return 0;
    
    std::vector<char> stack;
    size_t len = std::strlen(latex_str);
    
    for (size_t i = 0; i < len; ++i) {
        char c = latex_str[i];
        
        // Escape sequence check (e.g. \{ or \})
        if (c == '\\' && i + 1 < len) {
            char next = latex_str[i + 1];
            if (next == '{' || next == '}' || next == '[' || next == ']') {
                i++; // Skip escaped literal bracket
                continue;
            }
        }
        
        if (c == '{' || c == '(' || c == '[') {
            stack.push_back(c);
        } else if (c == '}') {
            if (stack.empty() || stack.back() != '{') return 0;
            stack.pop_back();
        } else if (c == ')') {
            if (stack.empty() || stack.back() != '(') return 0;
            stack.pop_back();
        } else if (c == ']') {
            if (stack.empty() || stack.back() != '[') return 0;
            stack.pop_back();
        }
    }
    
    return stack.empty() ? 1 : 0;
}

int32_t khwarizmi_normalize_latex(const char* input_str, char* output_buf, int32_t max_out_len) {
    if (!input_str || !output_buf || max_out_len <= 0) return -1;
    
    std::string s(input_str);
    std::string out;
    out.reserve(s.size());
    
    bool in_space = false;
    for (size_t i = 0; i < s.size(); ++i) {
        char c = s[i];
        
        // Collapse multiple whitespaces
        if (std::isspace(static_cast<unsigned char>(c))) {
            if (!in_space && !out.empty() && out.back() != '{' && out.back() != '}' && out.back() != '\\') {
                out.push_back(' ');
                in_space = true;
            }
            continue;
        }
        in_space = false;
        
        // Normalize multiplication symbols (\cdot, \times, *)
        if (c == '*') {
            out += "\\cdot ";
            continue;
        }
        
        out.push_back(c);
    }
    
    // Trim trailing whitespace
    while (!out.empty() && std::isspace(static_cast<unsigned char>(out.back()))) {
        out.pop_back();
    }
    
    if (static_cast<int32_t>(out.size()) >= max_out_len) {
        return -1; // Buffer too small
    }
    
    std::memcpy(output_buf, out.c_str(), out.size());
    output_buf[out.size()] = '\0';
    return static_cast<int32_t>(out.size());
}

uint64_t khwarizmi_formula_hash(const char* latex_str) {
    if (!latex_str) return 0ULL;
    
    // 64-bit FNV-1a Hash
    uint64_t hash = 14695981039346656037ULL;
    const uint8_t* ptr = reinterpret_cast<const uint8_t*>(latex_str);
    
    while (*ptr) {
        if (!std::isspace(*ptr)) {
            hash ^= static_cast<uint64_t>(*ptr);
            hash *= 1099511628211ULL;
        }
        ptr++;
    }
    return hash;
}

}
