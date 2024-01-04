// <nowiki>
/*
 * SignpostTagger
 *
 * This gadget adds an window for editing tags for articles of The Signpost.
 * The tags are stored in Lua data modules and used to generate lists of
 * Signpost articles on the fly. Updating the modules manually would be
 * tedious, so this gadget simplifies the process.
 *
 * To install it, add the following to your personal .js page:
 
 importScript( 'User:Mr. Stradivarius/gadgets/SignpostTagger.js' ); // Linkback: [[User:Mr. Stradivarius/gadgets/SignpostTagger.js]]

 * Author: Mr. Stradivarius
 * License: Public domain
 * Inept hacking: JPxG
 * License: same lmao

 * Check this https://en.wikipedia.org/w/index.php?title=User:JPxG/SignpostTagger.js&diff=1191229063&oldid=1190092898
 * for HOT TIPZZZ on how to add functs to this

 */


mw.loader.using( [
	'mediawiki.api',
	'mediawiki.jqueryMsg',
	'mediawiki.Title',
	'mediawiki.util',
	'oojs-ui'
], function () {

"use strict";

/******************************************************************************
 *                           Default tags
 * 
 * The following object defines the tags that are loaded for an article when
 * that article does not yet have any article data. The properties (on the left
 * side) are the subpage names of the articles, and the values (on the right
 * side) are arrays of tag names.
 * 
 * When SignpostTagger is run on an article page, it checks the Signpost Lua
 * module for the year of the article to see if the article already has article
 * data. If it doesn't have any article data, then it compares the subpage name
 * of the article with the subpage names in the defaultTags object. If there is
 * a match, then it loads the corresponding tags.
 * 
 * Tags should be all lower case, with no punctuation or spaces. If a tag can
 * have multiple possible names, then you should use the canonical name here,
 * and you should add the other names as aliases in [[Module:Signpost/aliases]].
 ******************************************************************************/

var defaultTags = {
	'Arbitration report': [ 'arbitrationreport' ],
	'Blog': [ 'blogs' ],
	'Community view': [ 'communityview' ],
	'Discussion report': [ 'discussionreport' ],
	'Education report': [ 'educationreport' ],
	'Essay': [ 'essay' ],
	'Featured content': [ 'featuredcontent' ],
	'Features': [ 'featuredcontent' ],
	'Features and admins': [ 'featuredcontent', 'featuresandadmins', 'newadmins' ],
	'Forum': [ 'forum' ],
	'From the archives': [ 'fromthearchives' ],
	'From the editor': [ 'fromtheeditor' ],
	'From the editors': [ 'fromtheeditor' ],
	'Gallery': [ 'gallery' ],
	'Humour': [ 'humour' ],
	'News and notes': [ 'newsandnotes' ],
	'News from the WMF': [ 'newsfromthewmf' ],
	'In focus': [ 'infocus' ],
	'In review': [ 'inreview' ],
	'In the media': [ 'inthemedia' ],
	'In the news': [ 'inthemedia' ],
	'Interview': [ 'interviews' ],
	'Op-ed': [ 'opinion' ],
	'Op-Ed': [ 'opinion' ],
	'Opinion': [ 'opinion' ],
	'Recent research': [ 'recentresearch', 'research' ],
	'Special report': [ 'specialreport' ],
	'Technology report': [ 'tech', 'techreport' ],
	'Traffic report': [ 'statistics', 'traffic', 'trafficreport' ],
	'WikiProject report': [ 'wikiprojectreport', 'wikiprojects' ],
};

/******************************************************************************
 *                           MW config
 ******************************************************************************/

var config = mw.config.get( [
	'skin',
   	'wgAction',
	'wgArticleId',
	'wgNamespaceNumber',
	'wgTitle'
] );

// Quick exit for pages we definitely won't be working on.
if ( config.wgNamespaceNumber !== 4 || config.wgAction !== 'view' ) {
	return;
}

/******************************************************************************
 *                           currentPage object
 ******************************************************************************/

/**
 * Global object representing the current page.
 */
var currentPage = {
	text: config.wgTitle,
	namespace: config.wgNamespaceNumber,
	action: config.wgAction,
	exists: config.wgArticleId !== 0,
	skin: config.skin,

	/**
	 * @private
	 */
	_prefixedText: null,
	_year: null,
	_date: null,
	_subpage: null,
	_parsed: false,
	_isSignpostArticle: null
};

/**
 * Parse the page title and cache the results.
 *
 * @private
 */
currentPage._parseTitle = function () {
	var regex = /^Wikipedia Signpost\/((\d{4})-\d{2}-\d{2})\/([^\/]+)$/;
	var match = regex.exec( this.text );
	if ( match ) {
		this._isSignpostArticle = true;
		this._date = match[ 1 ];
		this._year = Number( match[ 2 ] );
		this._subpage = match[ 3 ];
	} else {
		this._isSignpostArticle = false;
	}
	this._parsed = true;
};

/**
 * Get the prefixed text.
 *
 * @return {string}
 */
currentPage.getPrefixedText = function () {
	if ( !this._prefixedText ) {
		this._prefixedText = mw.Title.newFromText(
			this.text,
			this.namespace
		).getPrefixedText();
	}
	return this._prefixedText;
};

/**
 * Get the year.
 *
 * @return {number}
 */
currentPage.getYear = function () {
	if ( !this._parsed ) {
		this._parseTitle();
	}
	return this._year;
};

/**
 * Get the date.
 *
 * @return {string}
 */
currentPage.getDate = function () {
	if ( !this._parsed ) {
		this._parseTitle();
	}
	return this._date;
};

/**
 * Get the subpage name.
 *
 * @return {string}
 */
currentPage.getSubpage = function () {
	if ( !this._parsed ) {
		this._parseTitle();
	}
	return this._subpage;
};

/**
 * Get the list of authors.
 *
 * @return {Array}
 */
currentPage.getAuthors = function () {
	var tx = String($( '#signpost-article-authors' ).text());
	if(tx.toLowerCase().substring(0, 3) == "by "){ tx = tx.substring(3); }
	tx = tx.replaceAll("\n", "")
	tx = tx.replaceAll(" & ", ", ")
	tx = tx.replaceAll(", and ", ", ")
	tx = tx.replaceAll(" and ", ", ");
    tx = tx.replaceAll("  ", " ");
	tx = tx.split(", ");
    return tx;
};

/**
 * Get the subhead from the RSS description.
 *
 * @return {string}
 */

 // Can also use document.getElementsByClassName("signpost-rss-description")[0].innerHTML
currentPage.getSubhead = function () {
	try {
			var sh = $( '.signpost-rss-description' )[0].innerHTML;

			// Strip out the heading from the RSS description text
			// which is almost always formatted as
			// "Heading: Subheading"
			var ti = currentPage.getArticleTitle();

			// Not EVERY instance of that string is the heading though.
			// Especially if the heading is short, or a single word:
			// we ONLY want to replace it if it appears right at the beginning.
			if (sh.indexOf(ti) === 0) {
				// almost always formatted as "Heading: Subheading"
				// but can be other stuff: let's check for all of them
				sh = sh.replace(ti + ": ", "");
				sh = sh.replace(ti + ":", "");
				sh = sh.replace(ti + " :", "");
				sh = sh.replace(ti, "");
			}

			return sh;
		} catch(error) {
			console.log(error);
			return "";
		}
};

/**
 * Get the piccy metadata from the header template.
 *
 * @return {Object}
 */
currentPage.getpiccydata = function () {
	var dict = {
		"filename": "",
		"credits":  "",
		"license":  "",
		"scaling":  "",
		"xoffset":  "",
		"yoffset":  ""
				}
	try {	
			dict["filename"] = $( '.signpost-piccyfilename' )[0].innerHTML;
			dict["credits"]  = $( '.signpost-piccy-credits' )[0].innerHTML;
			dict["license"]  = $( '.signpost-piccy-license' )[0].innerHTML;
			dict["scaling"]  = $( '.signpost-piccy-scaling' )[0].innerHTML;
			dict["xoffset"]  = $( '.signpost-piccy-xoffset' )[0].innerHTML;
			dict["yoffset"]  = $( '.signpost-piccy-yoffset' )[0].innerHTML;
			return dict;
		} catch(error) {
			console.log(error);
			return dict;
		}
};

/**
 * Whether this page is a Signpost article.
 *
 * @return {boolean}
 */
currentPage.isSignpostArticle = function () {
	if ( !this._parsed ) {
		this._parseTitle();
	}
	return this.namespace === 4 && this._isSignpostArticle;
};

/**
 * Whether this page is a redirect.
 *
 * @return {boolean}
 */
currentPage.isRedirect = function () {
	return /\bredirect=no\b/.test( window.location.search );
};

/**
 * Whether this page needs tagging.
 *
 * @return {boolean}
 */
currentPage.needsTagging = function () {
	return this.isSignpostArticle() &&
		this.action === 'view' &&
		this.exists &&
		!this.isRedirect();
};

/**
 * Find the article title by scraping the HTML of the current page.
 *
 * @return {string}
 */
currentPage.getArticleTitle = function () {
	var $h2, $span, title;

	// Try to get the title from the data-signpost-article-title attribute of
	// the element with ID "signpost-article-title". This is added by
	// [[Wikipedia:Wikipedia Signpost/Templates/Signpost-article-header-v2]].
	$h2 = $( '#signpost-article-title' );
	if ( $h2.length ) {
		title = $h2.attr( 'data-signpost-article-title' );
		if ( title && title.length > 0 ) {
			return title;
		}
	} else {
		// We couldn't find the title header, so just use the first header.
		$h2 = $( '#bodyContent h2:first' );
	}
	if ( !$h2.length ) {
		return '';
	}

	// Try to get the span containing the title text. This avoids any
	// "subscribe" or "edit section" links, etc.
	$span = $h2.find( 'span.mw-headline' );
	if ( $span.length ) {
		return $span.text();
	} else {
		return $h2.text();
	}
};

/**
 * Create a new window manager with one dialog and append it to the DOM.
 *
 * @param {Object} [dialog] A OOjs-ui window object
 * @return {Object} The window manager
 */
currentPage.initializeWindowManager = function ( dialog ) {
	var windowManager = new OO.ui.WindowManager();
	$( 'body' ).append( windowManager.$element );
	windowManager.addWindows( [ dialog ] );
	return windowManager;
};

/**
 * Add a Signpost portlet link that initializes a dialog.
 *
 * @param {Object} [dialog] A OOjs-ui window object
 */
currentPage.addSignpostPortlet = function ( dialog ) {
	var windowManager = this.initializeWindowManager( dialog );
	var location = this.skin === 'vector' ? 'p-views' : 'p-cactions';
	var portletLink = mw.util.addPortletLink(
		location,
		'#',
		'Manage tags',
		'ca-signpost-tagger',
		'Manage Signpost tags',
		'g',
		'#ca-watch'
	);
	$( portletLink ).click( function ( e ) {
		e.preventDefault();
		windowManager.openWindow( dialog );
	});
};

/******************************************************************************
 *                           LuaTitle class
 ******************************************************************************/

/**
 * Title in the Module namespace that houses Signpost index data.
 *
 * @class
 *
 * @constructor
 * @param {Object} [options] Configuration options
 */
var LuaTitle = function ( options ) {
	this.prefixedText = 'Module:' + options.title;
	this.title = new mw.Title( this.prefixedText );
	this.api = new mw.Api();
	this.content = null;
};

OO.initClass( LuaTitle );

LuaTitle.static.signpostModule = 'Signpost';

LuaTitle.static.luaRestrictedTokens = {
	'and': true,
	'break': true,
	'do': true,
	'else': true,
	'elseif': true,
	'end': true,
	'false': true,
	'for': true,
	'function': true,
	'if': true,
	'in': true,
	'local': true,
	'nil': true,
	'not': true,
	'or': true,
	'repeat': true,
	'return': true,
	'then': true,
	'true': true,
	'until': true,
	'while': true
};

LuaTitle.static.makeLuaString = function ( s ) {
	return '"' + s.replace( /(["\\])/g, '\\$1' ) + '"';
};

LuaTitle.prototype.getTitle = function () {
	return this.title;
};

/* Load the Lua module and return its contents as a JavaScript object.
 *
 * @return {promise}
 */
LuaTitle.prototype.load = function () {
	var luaTitle = this;
	var makeLuaString = LuaTitle.static.makeLuaString;

	return this.api.postWithToken( 'csrf', {
		action: 'scribunto-console',
		format: 'json',
		title: luaTitle.constructor.static.signpostModule,
		question: "local success, ret = pcall( require, " + makeLuaString( this.prefixedText ) + " )\n" +
			"if success then\n" +
			"    print( mw.text.jsonEncode( { hasError = false, error = '', result = ret } ) )\n" +
			"else\n" +
			"    print( mw.text.jsonEncode( { hasError = true, error = ret, result = nil } ) )\n" +
			"end"
	} ).then( function ( obj ) {
		return $.Deferred( function ( deferred ) {
			if ( obj.type === 'normal' ) {
				// Lua command succeeded
				try {
					var response = JSON.parse( obj.print );
				} catch ( e ) {
					// There was a problem parsing the JSON data from Lua
					return deferred.reject(
						'luajsonparseerror',
						{ error: {
							code: 'luajsonparseerror',
							info: e.message
						} },
						{ recoverable: false, title: luaTitle.getTitle() }
					);
				}
				if ( !response.hasError ) {
					// We got the content successfully
					return deferred.resolve( response.result );
				} else if ( response.error.search( /module '.*' not found/ ) ) {
					// The module does not exist
					return deferred.reject(
						'luamodulenotfound',
						{ error: {
							code: 'luamodulenotfound',
							info: response.error
						} },
						{ recoverable: true, title: luaTitle.getTitle() }
					);
				} else {
					// The Lua require call failed for some other reason
					return deferred.reject(
						'luarequireerror',
						{ error: {
							code: 'luarequireerror',
							info: response.error
						} },
						{ recoverable: false, title: luaTitle.getTitle() }
					);
				}
			} else if ( obj.type === 'error' ) {
				// Lua command failed but API call succeeded
				return deferred.reject(
					'luacommandfailed',
					{ error: {
						code: 'luacommandfailed',
						info: obj.message
					} },
					{ recoverable: false, title: luaTitle.getTitle() }
				);
			} else if ( obj.error ) {
				// API call failed
				return deferred.reject( obj.error.code, obj );
			} else {
				return deferred.reject(
					'unknownapiresponse',
					{ error: {
						code: 'unknownapiresponse',
						info: 'Unknown API response'
					} }
				);
			}
		} ).promise();
	} );
};

/** 
 * Turn a javascript value into the equivalent Lua code, and set it in the
 * object. Values can be nested, and can be strings, numbers, booleans, arrays,
 * and objects. Arrays and objects cannot contain self-references; doing so will
 * result in an infinite loop.
 *
 * @param {Object} data
 */
LuaTitle.prototype.setContent = function ( options ) {
	options = options || {};
	var makeLuaString = LuaTitle.static.makeLuaString;

	function makeLuaTableKey( s ) {
		if (
			s.match( /^[_a-zA-Z][_a-zA-Z0-9]*$/ ) && // Basic Lua name requirements
			!s.match( /^_[A-Z]+$/ ) && // Reserved for internal Lua use
			!LuaTitle.static.luaRestrictedTokens[ s ]
		) {
			return s;
		} else {
			return '[' + makeLuaString( s ) + ']';
		}
	}

	function isOneLine( val, indent ) {
		for ( var i = 0, len = val.length; i < len; i++ ) {
			if ( typeof val[ i ] === 'object' ) {
				return false;
			}
		}
		return indent >= 2;
	}

	function repeatPush( arr, s, n ) {
		for ( var i = 0; i < n; i++ ) {
			arr.push( s );
		}
	}

	function pushLuaArray( val, ret, indent ) {
		var i, len;
		var oneLine = isOneLine( val, indent );
		var nextIndent = indent + 1;
		ret.push( '{' );
		for ( i = 0, len = val.length; i < len; i++ ) {
			if ( oneLine ) {
				pushLuaCode( val[ i ], ret, nextIndent );
				if ( i < len - 1 ) {
					ret.push( ', ' );
				}
			} else {
				ret.push( '\n' );
				repeatPush( ret, '\t', nextIndent );
				pushLuaCode( val[ i ], ret, nextIndent );
				ret.push( ',' );
			}
		}
		if ( !oneLine ) {
			ret.push( '\n' );
			repeatPush( ret, '\t', indent );
		}
		ret.push( '}' );
	}

	function pushLuaTable( val, ret, indent ) {
		var i, p, len;
		var oneLine = isOneLine( val, indent );
		var nextIndent = indent + 1;
		var props = [];
		ret.push( '{' );
		for ( p in val ) {
			if ( val.hasOwnProperty( p ) ) {
				props.push( p );
			}
		}
		props.sort( options.sortFunc );
		for ( i = 0, len = props.length; i < len; i++ ) {
			p = props[ i ];
			if ( !oneLine ) {
				ret.push( '\n' );
				repeatPush( ret, '\t', nextIndent );
			}
			ret.push( makeLuaTableKey( p ) );
			ret.push( ' = ' );
			pushLuaCode( val[ p ], ret, nextIndent );
			if ( !oneLine ) {
				ret.push( ',' );
			} else if ( i < len - 1 ) {
				ret.push( ', ' );
			}
		}
		if ( !oneLine ) {
			ret.push( '\n' );
			repeatPush( ret, '\t', indent );
		}
		ret.push( '}' );
	}
 
	function pushLuaCode( val, ret, indent ) {
		var tp = typeof val;
		if ( tp == 'string' ) {
			ret.push( makeLuaString( val ) );
		} else if ( tp == 'number' ) {
			ret.push( val );
		} else if ( tp == 'boolean' ) {
			ret.push( String( val ) );
		} else if ( $.isArray( val ) ) {
			pushLuaArray( val, ret, indent );
		} else if ( tp == 'object' ) {
			pushLuaTable( val, ret, indent );
		} else {
			throw new Error( 'setContent data values must be strings, numbers, booleans, arrays, or objects (' + tp + ' detected)' );
		}
	}
 
	var luaCode = [ 'return ' ];
	pushLuaCode( options.data, luaCode, 0 );
	this.content = luaCode.join( '' );
};

/* Save the page.
 *
 * @param {string} s The string to save
 * @param {string} summary A custom edit summary
 *
 * @return {promise}
 */
LuaTitle.prototype.save = function ( options ) {
	if ( !this.content ) {
		throw new Error( 'no content has been set; use the setContent method');
	}
	var summary = options.summary || 'update Signpost data';
	summary += ' ([[WP:SPT|SPT]])';
	return this.api.postWithToken( 'csrf', {
		format: 'json',
		action: 'edit',
		title: this.prefixedText,
		summary: summary,
		contentmodel: 'Scribunto',
		text: this.content
	} );
};

/******************************************************************************
 *                           LuaYearIndex class
 ******************************************************************************/

var LuaYearIndex = function ( options ) {
	options = options || {};
	options.title = LuaYearIndex.parent.static.signpostModule +
		'/index/' +
		options.year.toString();
	LuaYearIndex.super.call( this, options );
};

OO.inheritClass( LuaYearIndex, LuaTitle );

LuaYearIndex.static.sortKeys = {
	date:    0,
	subpage: 1,
	title:   2,
	subhead: 3,
	authors: 4,
	piccy:   5,
	tags:    6,
	views:   7
};

/* Load and validate the index module data.
 *
 * @return {jquery.promise}
 */
LuaYearIndex.prototype.load = function () {
	var luaTitle = this;

	var isString = function ( val ) {
		return val.constructor === String;
	};

	var isMaybeString = function ( val ) {
		return val === undefined || isString( val );
	};

	var isDate = function ( s ) {
		return /^\d{4}-\d{2}-\d{2}$/.test( s );
	};

	var isValidSubpage = function ( s ) {
		return s.length > 0;
	};

	var formatObjError = function ( i, what, expectType ) {
		return what + ' in object #' + i + ' is not a ' + expectType;
	};

	var rejectDeferred = function ( deferred, code, message ) {
		return deferred.reject(
			code,
			{ error: {
				code: code,
				info: message
			} },
			{ recoverable: false, title: luaTitle.getTitle() }
		);
	};

	return LuaYearIndex.super.prototype.load.call( this ).then(
		// On success
		function ( data ) {
			return $.Deferred( function ( deferred ) {
				if ( !$.isArray( data ) ) {
					return rejectDeferred(
						deferred,
						'indexcontainernotarray',
						'The outer index data container is not an array'
					);
				}
			
				var dataLength = data.length;
				for ( var i = 0; i < dataLength; i++ ) {
					var obj = data[ i ];
					var luaKey = i + 1;
			
					if ( typeof obj !== 'object' ) {
						return rejectDeferred(
							deferred,
							'indexvaluenotobject',
							'Value #' + luaKey + ' ' + 'in the index data is not an object'
						);
					} else if ( !isMaybeString( obj.title ) ) {
						return rejectDeferred(
							deferred,
							'indextitlenotstring',
							formatObjError( luaKey, 'The title property', 'string' )
						);
					} else if ( !isString( obj.date ) || !isDate( obj.date ) ) {
						return rejectDeferred(
							deferred,
							'invalidindexdate',
							formatObjError( luaKey, 'The date property', 'valid date' )
						);
					} else if ( !isString( obj.subpage ) || !isValidSubpage( obj.subpage ) ) {
						return rejectDeferred(
							deferred,
							'invalidindexsubpage',
							formatObjError( luaKey, 'The subpage property', 'valid subpage name' )
						);
					}
			
					var tags = obj.tags;
					if ( $.isArray( tags ) ) {
						var tagsLength = obj.tags.length;
						for ( var j = 0; j < tagsLength; j++ ) {
							if ( !isString( tags[ j ] ) ) {
								return rejectDeferred(
									deferred,
									'invalidindextag',
									formatObjError( luaKey, 'Tag #' + (j + 1), 'string' )
								);
							}
						}
					} else if ( obj.tags !== undefined ) {
						return rejectDeferred(
							deferred,
							'invalidindextagcontainer',
							'The tags property in object #' + luaKey + ' was defined but not an array'
						);
					}
				}
			
				return deferred.resolve( data );
			} ).promise();
		},
		// On error
		function ( code, errorObj, continuationObj ) {
			return $.Deferred( function ( deferred ) {
				if ( code === "luamodulenotfound" ) {
					// If a year index is not found, return an empty array
					return deferred.resolve( [] );
				} else {
					// If loading failed for another reason, pass the error on
					return deferred.reject( code, errorObj, continuationObj );
				}
			} ).promise();
		}
	);
};

LuaYearIndex.prototype.setContent = function ( options ) {
	options = typeof options === 'object' ? options : {};
	if ( options.sortFunc === undefined ) {
		options.sortFunc = function ( a, b ) {
			var aSort = LuaYearIndex.static.sortKeys[ a ];
			var bSort = LuaYearIndex.static.sortKeys[ b ];
			if ( aSort !== undefined && bSort !== undefined ) {
				return aSort < bSort ? -1 : 1;
			} else if ( aSort !== undefined ) {
				return -1;
			} else if ( bSort !== undefined ) {
				return 1;
			} else {
				return a < b ? -1 : 1;
			}
		};
	}
	LuaYearIndex.super.prototype.setContent.call( this, options );
};

/******************************************************************************
 *                           LuaAliases class
 ******************************************************************************/

var LuaAliases = function ( options ) {
	options = options || {};
	options.title = LuaYearIndex.parent.static.signpostModule + '/aliases';
	LuaAliases.super.call( this, options );
};

OO.inheritClass( LuaAliases, LuaTitle );


/* Load and validate the aliases module data.
 *
 * @return {jquery.promise}
 */
LuaAliases.prototype.load = function () {
	var luaAliases = this;

	var rejectDeferred = function ( deferred, code, message ) {
		return deferred.reject(
			code,
			{ error: {
				code: code,
				info: message
			} },
			{ recoverable: false, title: luaAliases.getTitle() }
		);
	};

	return LuaAliases.super.prototype.load.call( this ).then( function ( data ) {
		return $.Deferred( function ( deferred ) {
			var tag, aliases, i, len, alias;

			if ( typeof data !== 'object' || $.isArray( data ) ) {
				return rejectDeferred(
					deferred,
					'aliasescontainernotobject',
					'The outer aliases data container is not an object'
				);
			}

			for ( tag in data ) {
				if ( data.hasOwnProperty( tag ) ) {
					aliases = data[ tag ];

					if ( !$.isArray( aliases ) ) {
						return rejectDeferred(
							deferred,
							'aliasesnotarray',
							"The value for tag '" + tag + "' was not an array"
						);
					}

					for ( i = 0, len = aliases.length; i < len; i++ ) {
						alias = aliases[ i ];
						if ( typeof alias !== 'string' ) {
							return rejectDeferred(
								deferred,
								'aliasnotstring',
								"Alias #" + i + " for tag '" + tag + "' was not a string"
							);
						}
					}
				}
			}

			return deferred.resolve( data );
		} ).promise();
	} );
};

/******************************************************************************
 *                          TagManager class
 ******************************************************************************/

/**
 * Class for managing tags for the current page.
 *
 * @class
 *
 * @constructor
 * @param {Object} [config] Configuration options
 */
var TagManager = function () {
	this.luaYearIndex = new LuaYearIndex( { year: currentPage.getYear() } );
	this.luaAliases = new LuaAliases();
	this.title = '';
	this.tags = '';
	this.aliases = null;
	this.loaded = false;
	this.broken = false;
	this.indexData = null;
	this.articleExists = false;
	this.articleData = null;
	this.articleExistedOriginally = false;
	this.originalArticleData = null;
};

OO.initClass( TagManager );

// Regex to strip all punctuation characters and all whitespace from tag strings.
TagManager.static.tagNormalizerRegex = /[\u2000-\u206F\u2E00-\u2E7F\\'!"#\$%&\(\)\*\+,\-\.\/:;<=>\?@\[\]\^_`\{\|\}~\s]/g;

TagManager.prototype.getTitle = function () {
	return this.title;
};

TagManager.prototype.setTitle = function ( val ) {
	this.title = val;
};

TagManager.prototype.getTags = function () {
	return this.tags;
};

TagManager.prototype.setTags = function ( val ) {
	this.tags = val;
};

TagManager.prototype.isBroken = function () {
	return this.broken;
};

TagManager.prototype.isLoaded = function () {
	return this.loaded;
};

TagManager.prototype.doesArticleExist = function () {
	return this.articleExists;
};

TagManager.prototype.getYearIndexTitle = function () {
	return this.luaYearIndex.getTitle();
};

/**
 * Whether the Lua title can be saved or not.
 *
 * @return {boolean}
 */
TagManager.prototype.isSavable = function () {
	var tags = this.normalizeTagString( this.getTags() );
	var title = this.normalizeTitleString( this.getTitle() );
	return !!title.length && (
		title !== this.originalArticleData.title ||
		tags !== this.originalArticleData.tags
	);
};

/**
 * Split a tag string into an array of tags.
 *
 * @param {string} s The tag string
 * @returns {Array}
 */
TagManager.prototype.splitTags = function ( s ) {
	var tagManager = this;
	var aliases = tagManager.aliases;
	var regex = tagManager.constructor.static.tagNormalizerRegex;
	return s.trim().split( /,/ ).map( function ( val ) {
		// Remove whitespace and punctuation
		val = val.toLowerCase().replace( regex, '' );
		// Normalize aliases
		return val && aliases[ val ] || val;
	} ).filter( function ( val, i, arr ) {
		// Remove blanks and duplicates
		return val && arr.indexOf( val ) === i;
	} ).sort( function ( s1, s2 ) {
		return s1.localeCompare( s2 );
	} );
};

/**
 * Join a tag array into a string, separated by commas.
 *
 * @param {Array} tags The tag array
 * @returns {string}
 */
TagManager.prototype.joinTags = function ( tags ) {
	return tags.join( ', ' );
};

/**
 * Normalize a tag string into one that can be tested for equality.
 * The result is the same format produced by TagManager.joinTags.
 *
 * @param {string} s The tag string
 * @returns string
 */
TagManager.prototype.normalizeTagString = function ( s ) {
	return this.joinTags( this.splitTags( s ) );
};

/**
 * Normalize a title string.
 *
 * @param {string} s The tag string
 * @returns string
 */
TagManager.prototype.normalizeTitleString = function ( s ) {
	return s.trim();
};

/**
 * Get the index data.
 */
TagManager.prototype.getIndexData = function () {
	return this.indexData || [];
};

/**
 * Set the index data.
 *
 * @param data
 */
TagManager.prototype.setIndexData = function ( data ) {
	data = data || [];
	this.indexData = data;
};

/**
 * Get the default tags for the current subpage.
 *
 * @return {string}
 */
TagManager.prototype.getDefaultTags = function () {
	var tags = defaultTags[ currentPage.getSubpage() ] || [];
	return this.joinTags( tags );
};

/**
 * Whether an article data object is the article data object for the current
 * page.
 *
 * @param {Object} obj
 * @return {boolean}
 */
TagManager.prototype.isCurrentArticleData = function ( obj ) {
	return obj.date === currentPage.getDate() && obj.subpage === currentPage.getSubpage();
};

/**
 * @return {jquery.promise}
 */
TagManager.prototype.loadData = function () {
	var aliasesPromise, allPromise;
	var tagManager = this;
	var indexPromise = tagManager.luaYearIndex.load();

	if ( tagManager.loaded ) {
		aliasesPromise = $.Deferred().resolve().promise();
	} else {
		aliasesPromise = this.luaAliases.load().then( function ( data ) {
			var tag, aliases, i, len, alias;
			tagManager.aliases = {};
			for ( tag in data ) {
				if ( data.hasOwnProperty( tag ) ) {
					aliases = data[ tag ];
					for ( i = 0, len = aliases.length; i < len; i++ ) {
						alias = aliases[ i ];
						tagManager.aliases[ alias ] = tag;
					}
				}
			}
		} );
	}

	allPromise = $.when( indexPromise, aliasesPromise );

	allPromise.fail( function ( code, data ) {
		tagManager.broken = true;
	} );

	return allPromise.then( function ( indexData ) {
		var filteredIndex, articleData, articleExists;

		// Set the index data.
		tagManager.indexData = indexData;

		// Find the article data.
		filteredIndex = indexData.filter( function ( obj ) {
			return tagManager.isCurrentArticleData( obj );
		} );
		articleData = filteredIndex[ 0 ];
		articleExists = !!articleData;

		// Normalize the article data.
		if ( articleData ) {
			articleData.title = tagManager.normalizeTitleString(
				articleData.title || ''
			);
			articleData.date = articleData.date || currentPage.getDate();
			articleData.subpage = articleData.subpage || currentPage.getSubpage();
			articleData.tags = articleData.tags || [];
			articleData.tags = tagManager.joinTags( articleData.tags );
		} else {
			articleData = {
				title: '',
				date: currentPage.getDate(),
				subpage: currentPage.getSubpage(),
				tags: ''
			};
		}

		// Set the article data.
		tagManager.articleExists = articleExists;
		tagManager.articleData = articleData;

		// Set things that should only be set on the first load.
		if ( !tagManager.loaded ) {
			tagManager.loaded = true;
			tagManager.articleExistedOriginally = articleExists;
			tagManager.originalArticleData = articleData;
			tagManager.setTitle( articleData.title || currentPage.getArticleTitle() );
			tagManager.setTags( articleData.tags || tagManager.getDefaultTags() );
		}
	} );
};

/**
 * Handle page saving.
 *
 * @param {Object} options
 * @return {jquery.promise}
 */
TagManager.prototype._saveIndexData = function ( options ) {
	var tagManager = this;
	return tagManager.loadData().then( function () {
		return $.Deferred( function ( deferred ) {
			var original = tagManager.originalArticleData;
			var latest = tagManager.articleData;

			// Check for edit conflicts.
			if ( tagManager.articleExists !== tagManager.articleExistedOriginally ||
					original.title !== latest.title ||
					original.date !== latest.date ||
					original.subpage !== latest.subpage ||
					original.tags !== latest.tags
			) {
				// We have an edit conflict.
				tagManager.broken = true;
				return deferred.reject(
					'spt-editconflict',
					{ error: {
						code: 'spt-editconflict',
						info: 'Edit conflict detected while saving tags'
					} },
					{ recoverable: false, title: tagManager.getYearIndexTitle() }
				);
			}

			// Create the new index data.
			var newIndexData;
			if ( options[ 'delete' ] ) {
				newIndexData = tagManager.getIndexData().filter( function ( obj ) {
					return !tagManager.isCurrentArticleData( obj );
				} );
			} else {
				newIndexData = tagManager.getIndexData().map( function ( obj ) {
					if ( !tagManager.isCurrentArticleData( obj ) ) {
						return obj;
					}
					var newObj = Object.assign({}, obj); // shallow copy
					newObj.title = tagManager.normalizeTitleString( tagManager.getTitle() );
					newObj.tags = tagManager.splitTags( tagManager.getTags() );
					newObj.date = currentPage.getDate();
					newObj.subpage = currentPage.getSubpage();
					newObj.authors = currentPage.getAuthors();
					newObj.subhead = currentPage.getSubhead();
					newObj.piccy = currentPage.getpiccydata();
					return newObj;
				} );
			}

			// Set the new index data and sort it.
			tagManager.indexData = newIndexData;
			tagManager.indexData.sort( function ( obj1, obj2 ) {
				if ( obj1.date < obj2.date ) {
					return -1;
				} else if ( obj1.date > obj2.date ) {
					return 1;
				} else {
					return obj1.subpage.localeCompare( obj2.subpage );
				}
			} );

			// Make the Lua code and save the page
			tagManager.luaYearIndex.setContent( {
				data: tagManager.indexData
			} );
			var savePromise = tagManager.luaYearIndex.save( {
				summary: options.summary
			} );

			savePromise.done( function () {
				deferred.resolve();
			} );

			savePromise.fail( function ( code, data ) {
				tagManager.broken = true;
				deferred.reject( code, data );
			} );
		} ).promise();
	} );
};

/**
 * @param {Object} options
 * @return {jquery.promise}
 */
TagManager.prototype.saveData = function () {
	var summary;
	if ( this.doesArticleExist() ) {
		summary = 'update Signpost data for [[' + currentPage.getPrefixedText() + ']]';
	} else {
		summary = 'create Signpost data for [[' + currentPage.getPrefixedText() + ']]';
	}
	return this._saveIndexData( {
		summary: summary
	} );
};

/**
 * @return {jquery.promise}
 */
TagManager.prototype.deleteData = function () {
	return this._saveIndexData( {
		'delete': true,
		summary: 'delete Signpost data for [[' + currentPage.getPrefixedText() + ']]'
	} );
};

TagManager.prototype.reset = function () {
	this.title = null;
	this.tags = null;
	this.loaded = false;
	this.broken = false;
	this.indexData = null;
	this.aliases = null;
	this.articleExists = false;
	this.articleData = null;
	this.articleExistedOriginally = false;
	this.originalArticleData = null;
};

/******************************************************************************
 *                              TagDialog class
 ******************************************************************************/

/**
 * TagDialog for editing Signpost article tags.
 *
 * @class
 * @abstract
 * @extends OO.ui.ProcessDialog
 *
 * @constructor
 * @param {Object} [config] Configuration options
 */
function TagDialog( config ) {
	config = config || {};
	config.size = 'large';
	this.tagManager = new TagManager();
	TagDialog.super.call( this, config ); // Parent constructor
}

/* Inheritance */

OO.inheritClass( TagDialog, OO.ui.ProcessDialog );

/* Static properties */

TagDialog.static.name = 'SignpostTaggerDialog';
TagDialog.static.title = 'Manage Signpost tags';

TagDialog.static.actions = [
	{ action: 'save', label: 'Save', flags: [ 'primary', 'constructive' ] },
	{ action: 'delete', label: 'Delete', flags: 'destructive' },
	{ label: 'Cancel', flags: 'safe' }
];

/**
 * Set custom height.
 */
TagDialog.prototype.getBodyHeight = function () {
	return 285;
};

/**
 * Initialize the dialog.
 */
TagDialog.prototype.initialize = function () {
	// Parent initalize method
	TagDialog.super.prototype.initialize.apply( this, arguments );

	// Initialize widgets
	this.panel = new OO.ui.PanelLayout( {
		$: this.$,
		padded: true,
		expanded: false
	} );
	this.fieldset = new OO.ui.FieldsetLayout( {
		$: this.$,
		classes: [ 'container' ]
	} );
	this.titleInput = new OO.ui.TextInputWidget( {
		$: this.$,
		placeholder: 'Insert the article title',
	} );
	this.tagInput = new OO.ui.TextInputWidget( {
		$: this.$,
		placeholder: 'Insert tags',
		selected: true,
	} );
	this.dateLabel = new OO.ui.LabelWidget( {
		$: this.$,
		label: $( '<span>' ).css( 'font-style', 'italic' ).text( currentPage.getDate() )
	} );
	this.subpageLabel = new OO.ui.LabelWidget( {
		$: this.$,
		label: $( '<span>' ).css( 'font-style', 'italic' ).text( currentPage.getSubpage() )
	} );
	this.authorsLabel = new OO.ui.LabelWidget( {
		$: this.$,
		label: this.makeAuthorList( currentPage.getAuthors() )
	} );
	this.subheadLabel = new OO.ui.LabelWidget( {
		$: this.$,
		label: $( '<span>' ).css( 'font-style', 'italic' ).text( currentPage.getSubhead() )
	} );

	this.piccyLabel = new OO.ui.LabelWidget( {
		$: this.$,
		label: $( '<span>' ).css( 'font-style', 'monospace' ).text( String(currentPage.getpiccydata()) )
	} );
	this.fieldset.addItems( [
		new OO.ui.FieldLayout( this.titleInput, {
			$: this.$,
			label: 'Title',
			align: 'top'
		} ),
		new OO.ui.FieldLayout( this.tagInput, {
			$: this.$,
			label: 'Tags (comma-separated)',
			align: 'top'
		} ),
		new OO.ui.FieldLayout( this.dateLabel, {
			$: this.$,
			label: 'Date',
			align: 'left'
		} ),
		new OO.ui.FieldLayout( this.subpageLabel, {
			$: this.$,
			label: 'Subpage',
			align: 'left'
		} ),
		new OO.ui.FieldLayout( this.authorsLabel, {
			$: this.$,
			label: 'Authors',
			align: 'left'
		} ),
		new OO.ui.FieldLayout( this.subheadLabel, {
			$: this.$,
			label: 'Subhead',
			align: 'left'
		} ),
		new OO.ui.FieldLayout( this.piccyLabel, {
			$: this.$,
			label: 'piccy',
			align: 'left'
		} )
	] );

	// Add widgets to the DOM
	this.panel.$element.append( this.fieldset.$element );
	this.$body.append( this.panel.$element );
};

/**
 * Make a list of article authors.
 *
 * @param {Array} authors An array of author usernames
 * @return {jQuery}
 */
TagDialog.prototype.makeAuthorList = function ( authors ) {
	var i, len, $authorList = $( '<span>' );
	for (i = 0, len = authors.length; i < len; i++ ) {
		$authorList.append( $( '<a>' )
			.attr( 'href', mw.Title.newFromText( authors[ i ], 2 ).getUrl() )
			.text( authors[ i ] )
		);
		if ( i + 1 < len ) {
			$authorList.append( ', ' );
		}
	}
	return $authorList;
};

/**
 * Call a method for all text input widgets.
 *
 * @param {string} method The method name
 * @param {Object} arg1 The first argument
 * @param {Object} arg2 The second argument
 */
TagDialog.prototype.setTextWidgetMethod = function ( method, arg1, arg2 ) {
	this.titleInput[ method ]( arg1, arg2 );
	this.tagInput[ method ]( arg1, arg2 );
};

/**
 * Disable all the dialog's content widgets.
 *
 * @param {boolean} disabled
 */
TagDialog.prototype.setDisabled = function ( disabled ) {
	this.setTextWidgetMethod( 'setDisabled', disabled );
	this.dateLabel.setDisabled( disabled );
	this.subpageLabel.setDisabled( disabled );
};

/**
 * Set the focus.
 */
TagDialog.prototype.setFocus = function () {
	if ( !this.titleInput.getValue() ) {
		this.titleInput.focus();
	} else {
		this.tagInput.focus();
	}
};

/**
 * Set the save ability.
 */
TagDialog.prototype.setSaveAbility = function () {
	this.actions.setAbilities( { save: this.tagManager.isSavable() } );
};

/**
 * Set the delete ability.
 */
TagDialog.prototype.setDeleteAbility = function () {
	this.actions.setAbilities( { "delete": this.tagManager.doesArticleExist() } );
};

/**
 * Handle text input.
 */
TagDialog.prototype.onTextInput = function () {
	this.tagManager.setTitle( this.titleInput.getValue() );
	this.tagManager.setTags( this.tagInput.getValue() );
	this.setSaveAbility();
};

/**
 * Handle enter presses on text input.
 */
TagDialog.prototype.onTextEnter = function () {
	if ( this.tagManager.isSavable() ) {
		this.executeAction( 'save' );
	}
};

/**
 * Make an OO.ui.Error object with nice formatting.
 *
 * @param {string} msg The error message
 * @param {Object} options
 *
 * @return {Object} the OO.ui.Error object
 */
TagDialog.prototype.makeError = function ( response, options ) {
	var titleObj, message, code, $selection, $small, sep, logTitle;
	var tagManager = this.tagManager;
	options = typeof options === 'object' ? options : {};

	function makeLink ( url, title, display ) {
		return $( '<a>' )
			.attr( 'href', url )
			.attr( 'title', title )
			.text( display );
	}

	function makeTitleLink ( titleObj, urlParams, display ) {
		return makeLink(
			titleObj.getUrl( urlParams ),
			titleObj.getPrefixedText(),
			display
		);
	}

	// Get the title object, if any.
	if ( typeof options.title === 'object' ) {
		titleObj = options.title;
	} else if ( typeof options.title === 'string' ) {
		titleObj = mw.Title.newFromText( options.title );
	}

	// Get the error message and code
	if ( typeof response === 'object' && response.error ) {
		message = response.error.info;
		code = response.error.code;
	} else if ( typeof response === 'string' ) {
		message = response;
		code = response;
	} else {
		message = 'An unknown error occurred';
		code = 'unknownerror';
	}

	// Set options for some known error types.
	if ( options.recoverable === undefined && code === 'hookaborted' ) {
		// We probably tried to save some invalid Lua.
		options.recoverable = false;
	}

	// Format the message
	$selection = $( '<div>' )
		.css( 'text-align', 'center' )
		.append( $( '<p>' )
			.append( $( '<strong>' )
				.addClass( 'error' )
				.text( message )
			)
		);

	// Add title links
	if ( titleObj ) {
		$small = $( '<small>' );
		sep = ' | ';
		logTitle = mw.Title.newFromText( 'Special:Log' );
		$small
			.append( 'Check data module: (' )
			.append( makeTitleLink( titleObj, null, 'view' ) )
			.append( sep )
			.append( makeTitleLink( titleObj, { action: 'edit' }, 'edit' ) )
			.append( sep )
			.append( makeTitleLink( titleObj, { action: 'history' }, 'history' ) )
			.append( sep )
			.append( makeLink(
				logTitle.getUrl( {
					page: titleObj.getPrefixedText()
				} ),
				logTitle.getPrefixedText(),
				'logs'
			) )
			.append( ')' );

		$selection.append( $( '<p>' ).append( $small ) );
	}

	return new OO.ui.Error( $selection, options );
};

/**
 * Handle pending status when making a network request.
 *
 * @param {jquery.promise}
 * @return {jquery.promise}
 */
TagDialog.prototype.setPending = function ( promise ) {
	var dialog = this;

	// Disable editing
	dialog.pushPending();
	dialog.setDisabled( true );
	dialog.actions.setAbilities( { save: false, "delete": false } );

	// Re-enable editing when events are no longer pending.
	promise.always( function () {
		dialog.popPending();
	} );

	return promise.then( null, function ( code, data, options ) {
		// Failure handler
		return [ dialog.makeError( data, options ) ];
	} );
};

/**
 * Handle load action.
 */
TagDialog.prototype.onLoad = function () {
	var dialog = this;
	var tagManager = dialog.tagManager;
	var promise = tagManager.loadData();
	promise.done( function () {
		// Set input fields
		dialog.titleInput.setValue( tagManager.getTitle() );
		dialog.tagInput.setValue( tagManager.getTags() );

		// Enable editing area
		dialog.setDisabled( false );
		dialog.setSaveAbility();
		dialog.setDeleteAbility();
		dialog.setFocus();

		// Connect event handlers
		dialog.setTextWidgetMethod( 'connect', dialog, {
			'change': 'onTextInput',
			'enter': 'onTextEnter'
		} );
	} );
	return dialog.setPending( promise );
};

/**
 * Override default ready process
 *
 * @param {Object} data
 */
TagDialog.prototype.getReadyProcess = function ( data ) {
	// Parent getReadyProcess method
	return TagDialog.super.prototype.getReadyProcess.call( this, data )
	.next( function () {
		// Trigger the load action once the dialog is set up.
		if ( this.tagManager.isLoaded() ) {
			this.setFocus();
			this.setSaveAbility();
			this.setDeleteAbility();
		} else {
			this.executeAction( 'load' );
		}
	}, this );
};

/**
 * Handle shared operations for saving and deleting pages.
 *
 * @param {Object} options
 */
TagDialog.prototype.onDataSave = function ( options ) {
	var dialog = this;
	options.promise.done( function () {
		// Close the window and issue a notification when it's done.
		var closePromise = dialog.close( { action: options.action } );
		closePromise.done( function () {
			var msgSetOptions = {};
			msgSetOptions[ options.notificationMessage ] = options.notificationText;
			mw.messages.set( msgSetOptions );
			mw.notify(
				mw.message( options.notificationMessage ),
				{ title: options.notificationTitle }
			);
		} );
	} );
	return dialog.setPending( options.promise );
};

/**
 * Handle saving.
 */
TagDialog.prototype.onSave = function () {
	var notification, messageKey;
	var yearIndexPrefixedText = this.tagManager.getYearIndexTitle().getPrefixedText();
	if ( this.tagManager.doesArticleExist() ) {
		notification = '[[' + yearIndexPrefixedText + ']] was updated.';
		messageKey = 'spt-data-updated';
	} else {
		notification = 'A new entry was created at [[' + yearIndexPrefixedText + ']].';
		messageKey = 'spt-data-created';
	}
	return this.onDataSave( {
		promise: this.tagManager.saveData(),
		action: 'save',
		notificationText: notification,
		notificationTitle: 'Signpost data saved',
		notificationMessage: messageKey
	} );
};

/**
 * Handle deleting.
 */
TagDialog.prototype.onDelete = function () {
	if ( !this.tagManager.doesArticleExist() ) {
		throw new Error( "Tried to delete but the article data doesn't exist" );
	}
	return this.onDataSave( {
		promise:  this.tagManager.deleteData(),
		action: 'delete',
		notificationText: 'The entry was removed from [[' +
			this.tagManager.getYearIndexTitle().getPrefixedText() +
			']].',
		notificationTitle: 'Signpost data deleted',
		notificationMessage: 'spt-data-deleted'
	} );
};

/**
 * Handle actions. This also handles the load action, which doesn't have a
 * dedicated button.
 */
TagDialog.prototype.getActionProcess = function ( action ) {
	return TagDialog.super.prototype.getActionProcess.call( this, action )
	.next( function () {
		if ( action === 'load' ) {
			return this.onLoad();
		} else if ( action === 'save' ) {
			return this.onSave();
		} else if ( action === 'delete' ) {
			return this.onDelete();
		} else {
			return TagDialog.super.prototype.getActionProcess.call( this, action );
		}
	}, this );
};

/**
 * Extend the default teardown process.
 */
TagDialog.prototype.getTeardownProcess = function ( data ) {
	return TagDialog.super.prototype.getTeardownProcess.call( this, data )
	.first( function () {
		if (
			this.tagManager.isBroken() ||
			data && ( data.action === 'save' || data.action === 'delete' )
		) {
			// Disconnect event handlers
			this.setTextWidgetMethod( 'disconnect', this, {
				'change': 'onTextInput',
				'enter': 'onTextEnter'
			} );

			// Reset everything.
			this.tagManager.reset();
			this.setTextWidgetMethod( 'setValue', '' );
		}
	}, this );
};

/******************************************************************************
 *                           Initialisation code
 ******************************************************************************/

function main() {
	if ( currentPage.needsTagging() ) {
		var dialog = new TagDialog();
		currentPage.addSignpostPortlet( dialog );
	}
}

main();

} );

// </nowiki>
