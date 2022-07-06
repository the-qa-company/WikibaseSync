<?php
/**
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 * @file
 */

namespace MediaWiki\Extension\WikibaseSync;
use Config;
use MediaWiki\ResourceLoader\Hook\ResourceLoaderGetConfigVarsHook;

global $wgUser;

class Hooks implements \MediaWiki\Hook\BeforePageDisplayHook{

	/**
	 * @see https://www.mediawiki.org/wiki/Manual:Hooks/BeforePageDisplay
	 * @param \OutputPage $out
	 * @param \Skin $skin
	 */
	public function onBeforePageDisplay( $out, $skin ): void {
		$user = \RequestContext::getMain()->getUser();
		if(!empty($user) && $user->getId() != 0){
			//var_dump(gettype($user));
			//var_dump($user->getId());
			$out->addModules( 'ext.wikibaseSync' );
		}
		$config = $out->getConfig();
	}

	public function onResourceLoaderGetConfigVars( array &$vars, $string, Config $config ): void {
		$vars['wgVisualEditor'] =[
			"wikibasesync_server_url" => $config->get( 'WikibaseSyncUrl' ),
			"PID" => $config->get( 'PID' ),
			"QID" => $config->get( 'QID' ),
		];
	}
}
