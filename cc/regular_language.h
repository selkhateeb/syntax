#include <string>
#include <iostream>
#include <memory>

using namespace std;

class Language;
typedef shared_ptr<Language> language_ptr;

class Language {
public:
  virtual bool is_match() { return false; }
  virtual bool is_terminal() { return false; }
  virtual language_ptr derive(char ch) = 0;
  virtual string to_lisp(string parent) = 0;

};


class Reject: public Language {
public:

  static shared_ptr<Reject> reject;
  bool is_terminal() { return true; }
  language_ptr derive(char ch);
  string to_lisp(string parent);
};


class Match: public Language {
public:

  static shared_ptr<Match> match;
  bool is_match() { return true; }
  bool is_terminal() { return true; }
  language_ptr derive(char ch);
  string to_lisp(string parent);
};

class Character: public Language {
public:
  char matching_char;

  Character(char);
  bool is_match() { return false; }
  bool is_terminal() { return true; }
  language_ptr derive(char ch);
  string to_lisp(string parent);
};



class Or: public Language {
public:
  language_ptr left;
  language_ptr right;

  Or(language_ptr left, language_ptr right);
  bool is_match();
  language_ptr derive(char ch);
  string to_lisp(string parent);

  static language_ptr make(language_ptr left, language_ptr right);
};



class And: public Language {
public:
  language_ptr left;
  language_ptr right;

  And(language_ptr left, language_ptr right);
  bool is_match();
  language_ptr derive(char ch);
  string to_lisp(string parent);

  static language_ptr make(language_ptr left, language_ptr right);
};


extern const language_ptr match;
extern const language_ptr reject;
