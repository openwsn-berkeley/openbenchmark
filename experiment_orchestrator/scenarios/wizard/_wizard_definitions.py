class Identifiers:
	dm = 'demo-scenario'
	ba = 'building-automation'
	ha = 'home-automation'
	im = 'industrial-monitoring'

class Roles:
	ms = 'monitoring-sensor'
	es = 'event-sensor'
	a  = 'actuator'
	ac = 'area-controller'
	zc = 'zone-controller'
	cu = 'control-unit'
	s  = 'sensor'
	bs = 'bursty-sensor'
	g  = 'gateway'


definitions = {

	Identifiers.dm: {
		Roles.ms: {
			'number': 50.0, 
			'nodes': [], 
			'dest_type': [Roles.cu], 
			'confirmable': {Roles.cu: False}, 
			'traffic_type': {Roles.cu: 'periodic'}, 
			'traffic_properties': {'interval': [180, 300]}, 
			'packets_in_burst': 1
		}, 
		Roles.a : {
			'number': 50.0, 
			'nodes': [], 
			'dest_type': [Roles.cu], 
			'confirmable': {Roles.cu: True},  
			'traffic_type': {Roles.cu: 'periodic'}, 
			'traffic_properties': {'interval': [180, 300]}, 
			'packets_in_burst': 1
		},
		Roles.cu: {
			'number': 1,
			'nodes': [], 
			'dest_type': [Roles.a], 
			'confirmable': {Roles.a: True},  
			'traffic_type': {Roles.a: 'poisson'},  
			'traffic_properties': {'mean': 10},             
			'packets_in_burst': 5
		}
	},

	Identifiers.ba: {   # Data per area except `zone-controller`
		Roles.ms: {
			'number': 3, 
			'nodes': [], 
			'dest_type': [Roles.ac],          
			'confirmable': {Roles.ac: True},        
			'traffic_type': {Roles.ac: 'periodic'}, 
			'traffic_properties': {'interval': [25, 35]},
			'packets_in_burst': 1   # seconds
		},   
		Roles.es: {
			'number': 4, 
			'nodes': [], 
			'dest_type': [Roles.ac],          
			'confirmable': {Roles.ac: True},        
			'traffic_type': {Roles.ac: 'poisson'},  
			'traffic_properties': {'mean': 10},               
			'packets_in_burst': 1   # per hour
		},   
		Roles.a : {
			'number': 2, 
			'nodes': [], 
			'dest_type': [Roles.ac],          
			'confirmable': {Roles.ac: True},        
			'traffic_type': {Roles.ac: 'periodic'}, 
			'traffic_properties': {'interval': [25, 35]},     
			'packets_in_burst': 1
		}, 
		Roles.ac: {
			'number': 1, 
			'nodes': [], 
			'dest_type': [Roles.a, Roles.zc], 
			'confirmable': {Roles.a: True, Roles.zc: False}, 
			'traffic_type': {Roles.a: 'poisson', Roles.zc: 'periodic'}, 
			'traffic_properties': {'mean': 10, 'interval': [0.12, 0.14]}, 
			'packets_in_burst': 1
		},
		Roles.zc: {
			'number': 1, 
			'nodes': [], 
			'dest_type': None,
			'traffic_type': None
		}
	},

	Identifiers.ha: {   # All % except control-unit
		Roles.ms: {
			'number': 49.0, 
			'nodes': [], 
			'dest_type': [Roles.cu], 
			'confirmable': {Roles.cu: False}, 
			'traffic_type': {Roles.cu: 'periodic'}, 
			'traffic_properties': {'interval': [180, 300]}, 
			'packets_in_burst': 1
		}, 
		Roles.es: {
			'number': 21.0, 
			'nodes': [], 
			'dest_type': [Roles.cu], 
			'confirmable': {Roles.cu: True},  
			'traffic_type': {Roles.cu: 'poisson'},  
			'traffic_properties': {'mean': 10},             
			'packets_in_burst': 1
		}, 
		Roles.a : {
			'number': 30.0, 
			'nodes': [], 
			'dest_type': [Roles.cu], 
			'confirmable': {Roles.cu: True},  
			'traffic_type': {Roles.cu: 'periodic'}, 
			'traffic_properties': {'interval': [180, 300]}, 
			'packets_in_burst': 1
		}, 
		Roles.cu: {
			'number': 1,
			'nodes': [], 
			'dest_type': [Roles.a], 
			'confirmable': {Roles.a: True},  
			'traffic_type': {Roles.a: 'poisson'},  
			'traffic_properties': {'mean': 10},             
			'packets_in_burst': 5
		}
	},

	Identifiers.im : {   # All % except gateway
		Roles.s : {
			'number': 90.0, 
			'nodes': [], 
			'dest_type': [Roles.g], 
			'confirmable': {Roles.g: False}, 
			'traffic_type': {Roles.g: 'periodic'}, 
			'traffic_properties': {'interval': [1, 60]},    
			'packets_in_burst': 1
		}, 
		Roles.bs: {
			'number': 10.0, 
			'nodes': [], 
			'dest_type': [Roles.g], 
			'confirmable': {Roles.g: False}, 
			'traffic_type': {Roles.g: 'periodic'}, 
			'traffic_properties': {'interval': [60, 3600]}, 
			'packets_in_burst': 1
		}, 
		Roles.g : {
			'number': 1,    
			'nodes': [], 
			'dest_type': None,                              
			'traffic_type': None
		}				
	}

}