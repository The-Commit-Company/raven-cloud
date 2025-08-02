const common_site_config = require('../../../sites/common_site_config.json');
const { webserver_port } = common_site_config;

export default {
	// TODO: remove login from the list once we have a login page
	'^/(app|api/|assets|files|private|login)': {
		target: `http://127.0.0.1:${webserver_port}`,
		ws: true,
		router: function(req) {
			const site_name = req.headers.host.split(':')[0];
			return `http://${site_name}:${webserver_port}`;
		}
	}
};
