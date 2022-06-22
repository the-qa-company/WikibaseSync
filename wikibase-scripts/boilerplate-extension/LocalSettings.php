<?php
/**
 * ----------------------------------------------------------------------------------------
 * This file is provided by the wikibase/wikibase docker image.
 * This file will be passed through envsubst which will replace "$" with "$".
 * If you want to change MediaWiki or Wikibase settings then either mount a file over this
 * template and or run a different entrypoint.
 * ----------------------------------------------------------------------------------------
 */

## Database settings
## Environment variables will be substituted in here.
$wgDBserver = "mysql.svc:3306";
$wgDBname = "my_wiki";
$wgDBuser = "sqluser";
$wgDBpassword = "change-this-sqlpassword";

## Logs
## Save these logs inside the container
$wgDebugLogGroups = array(
	'resourceloader' => '/var/log/mediawiki/resourceloader.log',
	'exception' => '/var/log/mediawiki/exception.log',
	'error' => '/var/log/mediawiki/error.log',
);

## Site Settings
# TODO pass in the rest of this with env vars?
$wgServer = WebRequest::detectServer();
$wgShellLocale = "en_US.utf8";
$wgLanguageCode = "en";
$wgSitename = "wikibase-docker";
$wgMetaNamespace = "Project";
# Configured web paths & short URLs
# This allows use of the /wiki/* path
## https://www.mediawiki.org/wiki/Manual:Short_URL
$wgScriptPath = "/w";        // this should already have been configured this way
$wgArticlePath = "/wiki/$1";


#Set Secret
$wgSecretKey = "some-secret-key";

## RC Age
# https://www.mediawiki.org/wiki/Manual:
# Items in the recentchanges table are periodically purged; entries older than this many seconds will go.
# The query service (by default) loads data from recent changes
# Set this to 1 year to avoid any changes being removed from the RC table over a shorter period of time.
$wgRCMaxAge = 365 * 24 * 3600;

wfLoadSkin( 'Vector' );
wfLoadExtension( 'BoilerPlate' );
// T276905 - default set in Dockerfile
$wgJobRunRate = 0;

$wgEnableUploads = false;

$wgUploadDirectory = "/var/www/html/images";

## Wikibase Repository
wfLoadExtension( 'WikibaseRepository', "$IP/extensions/Wikibase/extension-repo.json" );
require_once "$IP/extensions/Wikibase/repo/ExampleSettings.php";

## Wikibase Client
wfLoadExtension( 'WikibaseClient', "$IP/extensions/Wikibase/extension-client.json" );
require_once "$IP/extensions/Wikibase/client/ExampleSettings.php";

#Pingback
$wgWBRepoSettings['wikibasePingback'] = false;

foreach (glob("LocalSettings.d/*.php") as $filename)
{
    include $filename;
}

//IMPORTANT FOR DESCRIPTIVE ERROR MESSAGES WHERE APPLICABLE
$wgShowExceptionDetails = true;

//IMPORTANT FOR BoilerPlate EXTENSION
$wgBoilerPlateWikibaseSyncConfig = ["local_server_url" => "http://127.0.0.1:5000", "PID" => "P1", "QID" => "P2"];
