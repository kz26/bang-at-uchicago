app.directive 'validatePassword', ->
	return {
		require: 'ngModel',
		link: (scope, elem, attrs, ctrl) ->
			scope.$watch (s) ->
				return s.$eval attrs.validateWith
			, ->
				if attrs.validateWith == ctrl.$viewValue
					ctrl.$setValidity('validatePassword', true)
				else
					ctrl.$setValidity('validatePassword', false)
			ctrl.$parsers.unshift (viewValue) ->
				pw1 = attrs.validateWith
				pw2 = viewValue
				if pw1 == pw2
					ctrl.$setValidity('validatePassword', true)
					return viewValue
				else
					ctrl.$setValidity('validatePassword', false)
					return undefined
	}

app.directive 'tooltip', ($parse) ->
	return {
		link: (scope, elem, attrs) ->
			if 'caption' of attrs
				attrs.$set 'title', $parse(attrs.caption)(scope)
			elem.tooltip()
	}

app.directive 'bool', ->
	return (scope, elem, attr) ->
		attr.$set('value', attr.bool == "true")
