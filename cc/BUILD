cc_binary(
  name = "syntax",
  deps = [":lexer"]
)
cc_library(
    name = "lexer",
    srcs = glob(["*.cc",], exclude = ["*_tests.cc"]),
    hdrs = glob(["*.h"]),
    visibility = ["//visibility:public"],
)

cc_test(
    name = "tests",
    size = "small",
    srcs = glob(["*_tests.cc"]),
    deps = ["//:lexer",
           "@googletest//:gtest_main"],
)
