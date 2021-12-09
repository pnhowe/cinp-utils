import os
from jinja2 import Environment

env = Environment()
header_template = env.from_string( """# Automatically generated by cinp-codegen from {{ url }} at {{ timestamp }}

from cinp import client

class {{ service }}( cinp.CInP ):
  def __init__( self, host, proxy=None ):
    super().__init__( host, '{{ root_path }}', proxy )
    ns = self.describe( '{{ root_path }}' )
    if ns[ 'api-version' ] != '{{ api_version }}':
      raise ValueError( 'API version mismatch.  Got "{0}", expected "{{ api_version }}"'.format( ns[ 'api-version' ] ) )
""" )

ns_template = env.from_string( """
  # Namespace {{ name }}({{ url }})
  \"\"\"
{{ doc }}
  \"\"\"
""" )

model_template = env.from_string( """{% set model_name = prefix|title + name %}
  # Model {{ model_name }}({{ url }})
  class {{ model_name }}:
   \"\"\"
{{ doc }}
   \"\"\"
   def __init__( self, id{% for field in fields %}, {{ field.name }}{% endfor %} ):
     self.__id = id
{% for field in fields %}      self.{{ field.name }} = {{ field.name }}
{% endfor %}

    @classmethod
    def list( cls, filter, filter_values ):
{% if not fitlers %}
      asdf
{% else %}
      if filter not in ( {% for filter in self.filters %}, '{{ filter.name }}'{% endfor %} ):
        raise ValueError( 'Invalid filter "{0}"'.format( filter ) )

{% endif %}

    @classmethod
    def get( cls, id ):
      data = cinp.get( '{{ url }}:{id}:'.format( id ) )

      return cls( id{% for field in fields %}, data[ '{{ field.name }}' ]{% endfor %} )

    @classmethod
    def create( cls{% for field in fields %}, {{ field.name }}{% endfor %} ):
      data = cinp.create( {% for field in fields %}, {{ field.name }}{% endfor %} )
      return cls( id{% for field in fields %}, data[ '{{ field.name }}' ]{% endfor %} )

    def update( self{% for field in fields %}, {{ field.name }}=None{% endfor %} ):
      cinp.update('{{ url }}:{id}:'.format( id ) )

    def delete( self ):
      pass

{% for action in actions %}
    def {{ action.name }}( self{% for paramater in action.paramaters %}, {{ paramater.name }}{% endfor %} ):
{% if action.static %}
      return ---cinp.call( {{ action.url }}{% for paramater in action.paramaters %}, {{ paramater.name }}{% endfor %} )
{% else %}
      return cinp.call( {{ action.url }}{% for paramater in action.paramaters %}, {{ paramater.name }}{% endfor %} )
{% endif %}
{% endfor %}
""")


def write_model( fp, prefix, model ):
  value_map = {
                'prefix': prefix,
                'name': model[ 'name' ],
                'url': model[ 'url' ],
                'doc': model[ 'doc' ]
              }

  fp.write( model_template.render( **value_map ) )


def write_namespace( fp, prefix, namespace ):
  value_map = {
                'name': namespace[ 'name' ],
                'url': namespace[ 'url' ],
                'doc': namespace[ 'doc' ]
              }
  fp.write( ns_template.render( **value_map ) )

  for model in namespace[ 'model_list' ]:
    write_model( fp, prefix, model )

  for child in namespace[ 'namespace_list' ]:
    write_namespace( fp, '{0}_{1}'.format( prefix, namespace[ 'name' ] ), child )


def python_render_func( wrk_dir, header_map, root ):
  header_map[ 'api_version' ] = root[ 'api_version' ]
  root[ 'name' ] = ''

  with open( os.path.join( wrk_dir, '{0}.py'.format( header_map[ 'service' ] ) ), 'w' ) as fp:  # TODO: make sure this is filsystem safe
    fp.write( header_template.render( **header_map ) )
    write_namespace( fp, '', root )
