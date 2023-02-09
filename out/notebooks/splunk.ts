import * as splunk from 'splunk-sdk';
import * as vscode from 'vscode'

export function getClient() {
    const config = vscode.workspace.getConfiguration();
    const restUrl = config.get<string>('splunk.commands.splunkRestUrl');
    const token = config.get<string>('splunk.commands.token');

    let url = new URL(restUrl);
    const scheme = url.protocol.replace(':', '');
    const port = url.port;
    const host = url.hostname;

    let service = new splunk.Service({
        scheme: scheme,
        host: host,
        port: port,
        sessionKey: token,
        version: '8',
        authorization: 'Bearer',
    });

    return service
}

export function splunkLogin(service) {

    return new Promise(function(resolve, reject) {
        
        service.login(function(err, wasSuccessful) {
            if (err !== null || !wasSuccessful) {
                reject(err)
            } else {
                resolve(null)
            }
        })

    })


}


export function createSearchJob(jobs, query, options) {

    return new Promise(function(resolve, reject) {
        jobs.create(query, options, function(err, data) {
            if (err !== null) {
                reject(err);
            } else {
                resolve(data)
            }
        })

    })
}

export function getSearchJobBySid(service, sid) {
    return new Promise(function(resolve, reject) {
        service.getJob(sid, function(err, data) {
            if (err != null) {
                reject(err)
            } else {
                resolve(data)
            }
        })
    })
}


export function getSearchJob(job) {
    return new Promise(function(resolve, reject) {
        job.fetch(function(err, job) {
            if (err !== null) {
                reject(err)
            } else {
                resolve(job)
            }
        })

    })
}

export function getJobSearchLog(job) {
    return new Promise(function(resolve, reject) {
        job.searchlog(function(err, log) {
            if (err !== null) {
                reject(err)
            } else {
                resolve(log)
            }
        })

    })
}

export function getSearchJobResults(job) {
    return new Promise(function(resolve, reject) {
        job.get("results", {"output_mode": "json_cols"},function(err, results) {
            if (err !== null) {
                reject(err)
            } else {
                resolve(results)
            }
        })

    })
}

export function cancelSearchJob(job) {
    return new Promise(function(resolve, reject) {
        job.cancel(function(err, results) {
            if (err !== null) {
                reject(err)
            } else {
                resolve(results)
            }

        })
    })
}

export function wait(ms = 1000) {
    return new Promise(resolve => {
      setTimeout(resolve, ms);
    });
}