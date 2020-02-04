import os
from jinja2 import Environment

env = Environment()
service_template = env.from_string( """// Automatically generated by cinp-codegen from {{url}} at {{timestamp}}

package {{service}}

import (
	"fmt"

	cinp "github.com/cinp/go"
)

const apiVersion = "{{api_version}}"

// {{service|title}} from {{url}}
type {{service|title}} struct {
	cinp *cinp.CInP
}

// New{{service|title}} creates and returns a new {{service|title}}
func New{{service|title}}(host string, proxy string) (*{{service|title}}, error) {
	var err error
	s := {{service|title}}{}
	s.cinp, err = cinp.NewCInP(host, "{{root_path}}", proxy)
	if err != nil {
		return nil, err
	}

  r, _, err := s.cinp.Describe("/api/v1/")
	if err != nil {
		return nil, err
	}

	if r.APIVersion != apiVersion {
		return nil, fmt.Errorf("Contractor API version mismatch.  Got '%s', expected '%s'", r.APIVersion, apiVersion)
	}

	return &s, nil
}

// SetAuth setts the authencation id and token
func (s *{{service|title}}) SetAuth(authID string, authToken string) {
  s.cinp.SetAuth(authID, authToken)
}
""" )  # noqa

ns_template = env.from_string( """
	// {{name}} from {{url}}
	type {{name}} struct {
""" )  # noqa

model_template = env.from_string( """

		//{{name}}({{url}}) - {{doc}}
		/*
{{ doc }}
		*/
		type {{name}} struct {
{% for field in fields %}
			{{ field.name }} string `json:"{{name}}"` // {{ field.type }}{% endfor %}
		}

		func {{name}}List(filterName string, filterValues map[string]interface{}, position int, count int) chan {{name}} {
			return cinp.ListObjectsChannel({{url}}, filterName, filterValues, postition, count)
		}


""")  # noqa
  # noqa


def service( wrk_dir, header_map ):
  open( os.path.join( wrk_dir, 'serivce.go' ), 'w' ).write( service_template.render( **header_map ) )


def do_namespace( wrk_dir, service, namespace, prefix ):
  filename = 'ns_{0}_{1}'.format( prefix, namespace[ 'name' ] )  # TODO: make sure this is filesystem safe
  value_map = {
                'service': service,
                'name': namespace[ 'name' ],
                'url': namespace[ 'url' ],
                'doc': namespace[ 'doc' ],
                'api_version': namespace[ 'api_version' ]
              }

  open( os.path.join( wrk_dir, filename ), 'w' ).write( service_template.render( **value_map ) )
  for child in namespace[ 'namespace_list' ]:
    do_namespace( wrk_dir, service, child, '{0}_{1}'.format( prefix, namespace[ 'name' ] ) )


def footer( value_map ):
  return footer_template.render( **value_map )


def nsHeader( value_map ):
  return ns_template.render( **value_map )


def nsFooter():
  return '	}'


def model( value_map ):
  return model_template.render( **value_map )


def go_render_func( wrk_dir, header_map, root ):
  header_map[ 'api_version' ] = root[ 'api_version' ]
  root[ 'name' ] = header_map[ 'service' ]
  service( wrk_dir, header_map )
  do_namespace( wrk_dir, header_map[ 'service' ], root, '' )
