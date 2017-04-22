# Standard setup.py, cf http://docs.python.org/distutils/index.html
#
# Usages:
#
# To prepare a release:
#   python setup.py sdist
#
# To install a release:
#   tar xzf EMVCAP-X.Y.tar.gz
#   cd EMVCAP-X.Y
#   python setup.py install

from distutils.core import setup
setup(name='EMVCAP',
      version='1.5',
      description='EMV-CAP device emulation script',
      long_description='This tool emulates an EMV-CAP device, to illustrate the article "Banque en ligne : a la decouverte d\'EMV-CAP" published in MISC, issue #56 and available online at http://www.unixgarden.com/index.php/misc/banques-en-ligne-a-la-decouverte-demv-cap',
      author='Philippe Teuwen & Jean-Pierre Szikora',
      author_email='phil@teuwen.org',
      url='http://sites.uclouvain.be/EMV-CAP/',
      license='Contrat Attribution-NoDerivs 2.0 Belgium http://creativecommons.org/licenses/by-nd/2.0/be/',
      py_modules=['EMVCAPcore', 'EMVCAPfoo'],
      scripts=['EMV-CAP'],
      requires=['argparse', 'pycrypto', 'pyscard']
      )
