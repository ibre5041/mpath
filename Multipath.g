// MIT License

// Copyright (c) 2017 Ivan Brezina

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

grammar Multipath;
options {
    output=AST;
    ASTLabelType=CommonTree; // type of $stat.tree ref etc...
    language=Python;

}

tokens { 
    MULTIPATH;
    HEXNUM;
}

// multipath.conf is the configuration file for the multipath daemon.
// It is used to overwrite the built-in configuration table of multipathd.
// Any line whose first non-white-space character is a '#' is considered a comment line. Empty lines are ignored.
// Syntax
//
// The configuration file contains entries of the form:
//
//     <section> {
//            <attribute> <value>
//            ...
//            <subsection> {
//                    <attribute> <value>
//                    ...
//            }
//     }

// Each section contains one or more attributes or subsections.
// The recognized keywords for attributes or subsections depend on the section in which they occor.

// The following section keywords are recognized:
DEFAULTS: 'defaults';

BLACKLIST: 'blacklist';

BLACKLIST_EXCEPTIONS: 'blacklist_exceptions';

MULTIPATHS: 'multipaths';

DEVICES: 'devices '; 

// The defaults section recognizes the following keywords:
POLLING_INTERVAL: 'polling_interval';
polling_interval: POLLING_INTERVAL^ NUMBER;

UDEV_DIR: 'udev_dir';
udev_dir: UDEV_DIR^ PATH;

MULTIPATH_DIR: 'multipath_dir';
multipath_dir: MULTIPATH_DIR^ PATH;

FIND_MULTIPATHS: 'find_multipaths';
find_multipaths: FIND_MULTIPATHS^ IDENTIFIER;

VERBOSITY: 'verbosity';
verbosity: VERBOSITY^ NUMBER;

PATH_SELECTOR: 'path_selector' | 'selector';
path_selector: PATH_SELECTOR^ STRING;

PATH_GROUPING_POLICY: 'path_grouping_policy';
path_grouping_policy: PATH_GROUPING_POLICY^ IDENTIFIER;

GETUID_CALLOUT: 'getuid_callout';
getuid_callout: GETUID_CALLOUT^ STRING;

// RHEL5? deprecated
PRIO_CALLOUT: 'prio_callout';
prio_callout: PRIO_CALLOUT^ STRING;

PRIO: 'prio';
prio: PRIO^ IDENTIFIER;

FEATURES: 'features';
features: FEATURES^ STRING;

PATH_CHECKER: 'path_checker' | 'checker';
path_checker: PATH_CHECKER^ IDENTIFIER;

FAILBACK: 'failback';
failback: FAILBACK^ (IDENTIFIER | NUMBER);

RR_MIN_IO: 'rr_min_io';
rr_min_io: RR_MIN_IO^ NUMBER;

RR_MIN_IO_RQ: 'rr_min_io_rq';
rr_min_io_rq: RR_MIN_IO_RQ^ NUMBER;

RR_WEIGHT: 'rr_weight';
rr_weight: RR_WEIGHT^ IDENTIFIER;

NO_PATH_RETRY: 'no_path_retry';
no_path_retry: NO_PATH_RETRY^ (NUMBER | IDENTIFIER);

USER_FRIENDLY_NAMES: 'user_friendly_names';
user_friendly_names: USER_FRIENDLY_NAMES^ IDENTIFIER;

QUEUE_WITHOUT_DAEMON: 'queue_without_daemon';
queue_without_daemon: QUEUE_WITHOUT_DAEMON^ IDENTIFIER;

FLUSH_ON_LAST_DEL: 'flush_on_last_del';
flush_on_last_del: FLUSH_ON_LAST_DEL^ IDENTIFIER;

MAX_FDS: 'max_fds';
max_fds: MAX_FDS^ NUMBER;

CHECKER_TIMEOUT: 'checker_timeout';
checker_timeout: CHECKER_TIMEOUT^ NUMBER;

FAST_IO_FAIL_TMO: 'fast_io_fail_tmo';
fast_io_fail_tmo: FAST_IO_FAIL_TMO^ (NUMBER | IDENTIFIER);

DEV_LOSS_TMO: 'dev_loss_tmo';
dev_loss_tmo: DEV_LOSS_TMO^ NUMBER;

HWTABLE_REGEX_MATCH: 'hwtable_regex_match';
hwtable_regex_match: HWTABLE_REGEX_MATCH^ IDENTIFIER;

//RESERVATION_KEY: 'reservation_key';

RETAIN_ATTACHED_HW_HANDLER: 'retain_attached_hw_handler';
retain_attached_hw_handler: RETAIN_ATTACHED_HW_HANDLER IDENTIFIER;

DETECT_PRIO: 'detect_prio';
detect_prio: DETECT_PRIO^ IDENTIFIER;

LOG_CHECKER_ERR: 'log_checker_err';
log_checker_err: LOG_CHECKER_ERR^ IDENTIFIER;

// blacklist section
WWID: 'wwid';
wwid: WWID^ (IDENTIFIER | STRING | HEXNUM | NUMBER);

// Regular expression of the device nodes to be excluded.
DEVNODE: 'devnode';
devnode: DEVNODE^ STRING;

DEVICE: 'device';

MULTIPATH: 'multipath';

//WWID: 'wwid';

ALIAS: 'alias';
alias: ALIAS^ (STRING | IDENTIFIER);

// devices section
// The only recognized attribute for the devices section is the device subsection.
//DEVICE: 'device';

// The device subsection recognizes the following attributes:
VENDOR: 'vendor';
vendor: VENDOR^ STRING;

PRODUCT: 'product';
product: PRODUCT^ STRING;

REVISION: 'revision';
revision: REVISION^ STRING;

PRODUCT_BLACKLIST: 'product_blacklist';
product_blacklist: PRODUCT_BLACKLIST^ product_blacklist;

HARDWARE_HANDLER: 'hardware_handler';
hardware_handler: HARDWARE_HANDLER^ STRING;

WS  :   (' '|'\t'|'\n'|'\r')+ {$channel = HIDDEN;};
COMMENT: '#' ~('\r' | '\n')* {$channel=HIDDEN;};

STRING :
'"' (~'"')* '"'
    ;

fragment DIGIT    : '0'..'9';
fragment HEXDIGIT : 'a'..'f' | 'A'..'F';

NUMBER : DIGIT
        ( DIGIT
        | HEXDIGIT { $type = HEXNUM; }
        )*
    ;

IDENTIFIER
: ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_'|'-')*;

PATH:
        '/' (IDENTIFIER | '/')*
    ;

multipath:
        (
            defaults_section
        |   blacklist_section
        |   blacklist_exceptions_section
        |   devices_section
        |   multipaths_section
        )*
        EOF
        -> ^(MULTIPATH defaults_section blacklist_section* blacklist_exceptions_section* devices_section* multipaths_section*)
    ;

defaults_section:
        DEFAULTS^
        '{'
        (
            polling_interval
        |   udev_dir
        |   multipath_dir
        |   find_multipaths
        |   verbosity
        |   path_selector
        |   path_grouping_policy
        |   getuid_callout
        |   prio_callout
        |   prio
        |   features
        |   path_checker
        |   failback
        |   rr_min_io
        |   rr_min_io_rq
        |   rr_weight
        |   no_path_retry
        |   user_friendly_names
        |   queue_without_daemon
        |   flush_on_last_del
        |   max_fds
        |   checker_timeout
        |   fast_io_fail_tmo
        |   dev_loss_tmo
        |   hwtable_regex_match
        |   retain_attached_hw_handler
        |   detect_prio
            // and some more (depending on DM_MULTIPATH version
            // https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/6/html/DM_Multipath/config_file_defaults.html
        )*
        '}'
    ;

blacklist_section:
        BLACKLIST^
        '{'
        (
            devnode
        |   device_section
        |   wwid
        )*
        '}'
    ;

blacklist_exceptions_section:
        BLACKLIST_EXCEPTIONS
        '{'
        (
            devnode
        |   device_section
        |   wwid
        )
        '}'
;

multipaths_section:
        MULTIPATHS^
        '{'
        multipath_section*
        '}';

multipath_section:
        MULTIPATH^
        '{'
        wwid?
        (
            alias
        |   path_grouping_policy
        |   path_selector
        |   failback
        |   prio
        |   no_path_retry
        |   rr_min_io
        |   rr_min_io_rq
        |   rr_weight
        |   flush_on_last_del
        |   path_checker
        //|   reservation_key
        )*
        '}'
    ;

devices_section:
        DEVICES^
        '{'
        device_section*
        '}'
    ;

device_section:
        DEVICE^
        '{'
        vendor
        product
        (
            revision 
        |   product_blacklist 
        |   hardware_handler                 
        |   path_grouping_policy
        |   getuid_callout
        |   path_selector
        |   features
        |   prio
        |   failback
        |   rr_weight
        |   no_path_retry
        |   rr_min_io
        |   rr_min_io_rq
        |   fast_io_fail_tmo
        |   dev_loss_tmo
        |   flush_on_last_del
        |   retain_attached_hw_handler
        |   detect_prio
        |   path_checker
        )*
        '}'
    ;
