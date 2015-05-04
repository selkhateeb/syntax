

class JavaClass(object):
    """Represents a java class.

    class Foo {}
    """

    def __init__(self, name):
        """
        Arguments:
        - `name`: class name.
        """
        self.name = name

        self.imports = []
        self.annotations = []

        self.extends = None
        self.interfaces = []

        self.fields = []
        self.methods = []




def java_class_printer(java_class):
    """Spits out characters that represents the passed java class.

    Arguments:
    - `java_class`: JavaClass object.
    """

    print 'class %s {}' % java_class.name


if __name__ == '__main__':
    java_class_printer(JavaClass('Foo'))
