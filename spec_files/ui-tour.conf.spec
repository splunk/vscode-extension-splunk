#   Version 7.3.0
#
# This file contains the tours available for Splunk Onboarding
#
# There is a default ui-tour.conf in $SPLUNK_HOME/etc/system/default. 
# To create custom tours, place a ui-tour.conf in
# $SPLUNK_HOME/etc/system/local/. To create custom tours for an app, place
# ui-tour.conf in $SPLUNK_HOME/etc/apps/<app_name>/local/.
#
# To learn more about configuration files (including precedence) see the
# documentation located at
# http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles
#
# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#   * You can also define global settings outside of any stanza, at the top of
#     the file.
#   * This is not a typical conf file for configurations. It is used to set/create
#     tours to demonstrate product functionality to users.
#   * If an attribute is defined at both the global level and in a specific
#     stanza, the value in the specific stanza takes precedence.

[<stanza name>]
* Stanza name is the name of the tour

useTour = <string>
* Used to redirect this tour to another when called by Splunk.
* Optional

nextTour = <string>
* String used to determine what tour to start when current tour is finished.
* Optional

intro = <string>
* A custom string used in a modal to describe what tour is about to be taken.
* Optional

type = <image || interactive>
* Can either be "image" or "interactive" to determine what kind of tour it is.
* Required

label = <string>
* The identifying name for this tour used in the tour creation app.
* Optional in general
* Required only if this tour is being to linked from another tour (nextTour)

tourPage = <string>
* The Splunk view this tour is associated with (only necessary if it is linked to).
* Optional

managerPage = <boolean>
* Used to signifiy that the tourPage is a manager page. This will change the url of
* when the tourPage is rendered to "/manager/{app}/{view}" rather than "/app/{app}/{view}"
* Optional

viewed = <boolean>
* A boolean to determine if this tour has been viewed by a user.
* Set by Splunk

skipText = <string>
* The string for the skip button (interactive and image)
* Defaults to "Skip tour"
* Optional

doneText = <string>
* The string for the button at the end of a tour (interactive and image)
* Defaults to "Try it now"
* Optional

doneURL = <string>
* The Splunk URL of where the user will be directed once the tour is over.
* The user will click a link/button.
* Helpful to use with above doneText attribute to specify location.
* Splunk link is formed after the localization portion of the full URL. For example if the link
* is localhost:8000/en-US/app/search/reports, the doneURL will be "app/search/reports"
* Optional

forceTour = <boolean>
* Used with auto tours to force users to take the tour and not be able to skip
* Optional

############################
## For image based tours
############################
# Users can list as many images with captions as they want. Each new image is created by
# incrementing the number.

imageName<int> = <string>
* The name of the image file (example.png)
* Required but Optional only after first is set

imageCaption<int> = <string>
* The caption string for corresponding image
* Optional

imgPath = <string>
* The subdirectory relative to Splunk's 'img' directory in which users put the images.
  This will be appended to the url for image access and not make a server request within Splunk.
  EX) If user puts images in a subdirectory 'foo': imgPath = foo.
  EX) If within an app, imgPath = foo will point to the app's img path of
      appserver/static/img/foo
* Required only if images are not in the main 'img' directory.

context = <system || <specific app name>>
* String consisting of either 'system' or the app name the tour images are to be stored.
* If set to 'system', it will revert to Splunk's native img path.
* Required


############################
## For interactive tours
############################
# Users can list as many steps with captions as they want. Each new step is created by
# incrementing the number.

urlData = <string>
* String of any querystring variables used with tourPage to create full url executing this tour.
* Don't add the "?" to the beginning of this string
* Optional

stepText<int> = <string>
* The string used in specified step to describe the UI being showcased.
* Required but Optional only after first is set

stepElement<int> = <selector>
* The UI Selector used for highlighting the DOM element for corresponding step.
* Optional

stepPosition<int> = <bottom || right || left || top>
* String that sets the position of the tooltip for corresponding step.
* Optional

stepClickEvent<int> = <click || mousedown || mouseup>
* Sets a specific click event for an element for corresponding step.
* Optional

stepClickElement<int> = <string>
* The UI selector used for a DOM element used in conjunction with click above.
* Optional
