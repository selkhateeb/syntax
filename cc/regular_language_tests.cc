#include "gtest/gtest.h"
#include "regular_language.h"

TEST(Character, match) {
  auto a = make_shared<Character>('a');
  ASSERT_EQ(a->derive('a'), match);
}

TEST(Character, reject) {
  auto a = make_shared<Character>('a');
  ASSERT_EQ(a->derive('b'), reject);
}


TEST(Or, derive) {
  auto a = make_shared<Character>('a');
  auto b = make_shared<Character>('b');
  auto r = Or::make(a, b);

  ASSERT_EQ(r->derive('a'), match);
  ASSERT_EQ(r->derive('b'), match);

  ASSERT_EQ(r->derive('c'), reject);
  ASSERT_EQ(r->derive('a')->derive('b'), reject);
}


TEST(And, derive) {
  auto a = make_shared<Character>('a');
  auto b = make_shared<Character>('b');
  auto r = And::make(a, b);

  ASSERT_EQ(r->derive('a')->derive('b'), match);
  ASSERT_EQ(r->derive('a')->derive('c'), reject);
  ASSERT_EQ(r->derive('b'), reject);
  ASSERT_EQ(r->derive('c'), reject);

}


int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
