#include <iostream>

#include "regular_language.h"


language_ptr Reject::derive(char ch) {
  return reject;
}

string Reject::to_lisp(string parent) { return "reject"; }
auto Reject::reject = make_shared<Reject>(Reject());



language_ptr Match::derive(char ch) {
  return reject;
}
string Match::to_lisp(string parent) { return "match"; }

auto Match::match = make_shared<Match>(Match());



Character::Character(char c): matching_char(c) {}
language_ptr Character::derive(char ch) {
  if (matching_char == ch) {
    return match;
  }
  return reject;
}
string Character::to_lisp(string parent) {
  return "'" + string(1, matching_char) + "'";
}



Or::Or(language_ptr l, language_ptr r):
  left(l), right(r) {};

bool Or::is_match() {
  return left->is_match() || right->is_match();
}

language_ptr Or::derive(char ch) {
  return make(left->derive(ch), right->derive(ch));
}

string Or::to_lisp(string parent) {
  return "(or " + left->to_lisp(parent) + " " + right->to_lisp(parent) + ")";
}

language_ptr Or::make(language_ptr left, language_ptr right) {
  if(left == match && right == match) {
    cout << "You got ambiguity in your grammar!!\n";
  }
  if(left == reject && right == reject) {
    return reject;
  } else if (left == reject) {
    return right;
  } else if (right == reject) {
    return left;
  } else if (left == match || right == match) {
    return match;
  }
  return make_shared<Or>(left, right);
}



And::And(language_ptr l, language_ptr r):
  left(l), right(r) {};

bool And::is_match() {
  return left->is_match() && right->is_match();
}

language_ptr And::derive(char ch) {
  if(left->is_match()) {
    Or::make(make(left->derive(ch), right), right->derive(ch));
  }
  return make(left->derive(ch), right);
}

string And::to_lisp(string parent) {
  return "(and " + left->to_lisp(parent) + " " + right->to_lisp(parent) + ")";
}

language_ptr And::make(language_ptr left, language_ptr right) {
  if(left == match) {
    return right;
  }

  if(left == reject || right == reject) {
    return reject;
  }

  return make_shared<And>(left, right);
}


const language_ptr match = Match::match;
const language_ptr reject = Reject::reject;
int main(int argc, char** argv) {
  auto a = make_shared<Character>('a');
  auto b = make_shared<Character>('b');
  auto c = make_shared<Character>('c');
  auto o = Or::make(a, b);

  auto oo = And::make(o, c);
  cout << oo->to_lisp("start") << endl;
  return 0;
}
