(define
    (domain bartender)
    (:requirements :strips)
    (:types )
    (:constants )
    (:predicates
        (know__drink)
        (know__size)
        (know__liquor)
        (know__mixer)
        (know__glass)
        (know__payment)
        (know__descriptors)
        (know__beverage)
        (know__require_drink_preferences)
        (require_drink_preferences)
        (know__require_drink_ingredients)
        (require_drink_ingredients)
        (informed)
        (know__goal)
        (goal)
        (force-statement)
    )
    (:action set-beverage
        :parameters()
        :precondition
            (and
                (require_drink_preferences)
                (not (know__beverage))
                (know__descriptors)
                (know__drink)
                (not (force-statement))
                (know__require_drink_preferences)
            )
        :effect
            (labeled-oneof set-beverage__assign_beverage
                (outcome set-red-wine
                    (and
                        (not (require_drink_preferences))
                        (know__beverage)
                    )
                )
                (outcome set-white-wine
                    (and
                        (not (require_drink_preferences))
                        (know__beverage)
                    )
                )
                (outcome set-lager
                    (and
                        (not (require_drink_preferences))
                        (know__beverage)
                    )
                )
                (outcome set-radler
                    (and
                        (not (require_drink_preferences))
                        (know__beverage)
                    )
                )
            )
    )
    (:action set-drink-requirements
        :parameters()
        :precondition
            (and
                (not (require_drink_preferences))
                (not (require_drink_ingredients))
                (not (know__require_drink_preferences))
                (not (know__descriptors))
                (not (know__require_drink_ingredients))
                (know__drink)
                (not (force-statement))
            )
        :effect
            (labeled-oneof set-drink-requirements__assign_requirements
                (outcome set-cocktail
                    (and
                        (force-statement)
                        (require_drink_ingredients)
                        (know__require_drink_ingredients)
                        (know__require_drink_preferences)
                    )
                )
                (outcome set-wine
                    (and
                        (force-statement)
                        (require_drink_preferences)
                        (know__require_drink_ingredients)
                        (know__require_drink_preferences)
                    )
                )
                (outcome set-beer
                    (and
                        (force-statement)
                        (require_drink_preferences)
                        (know__require_drink_ingredients)
                        (know__require_drink_preferences)
                    )
                )
            )
    )
    (:action get-liquor
        :parameters()
        :precondition
            (and
                (not (know__liquor))
                (know__drink)
                (require_drink_ingredients)
                (not (force-statement))
            )
        :effect
            (labeled-oneof get-liquor__set-liquor
                (outcome update_liquor
                    (and
                        (know__liquor)
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
    (:action get-mixer
        :parameters()
        :precondition
            (and
                (not (force-statement))
                (know__drink)
                (require_drink_ingredients)
                (know__liquor)
            )
        :effect
            (labeled-oneof get-mixer__set-mixer
                (outcome update_mixer
                    (and
                        (know__mixer)
                        (not (require_drink_ingredients))
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
    (:action get-descriptors
        :parameters()
        :precondition
            (and
                (know__drink)
                (not (force-statement))
                (require_drink_preferences)
            )
        :effect
            (labeled-oneof get-descriptors__set-descriptors
                (outcome update_descriptors
                    (and
                        (know__descriptors)
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
    (:action inform_beverage
        :parameters()
        :precondition
            (and
                (know__payment)
                (not (require_drink_preferences))
                (know__glass)
                (know__size)
                (not (informed))
                (know__beverage)
                (know__drink)
                (not (force-statement))
                (know__require_drink_preferences)
            )
        :effect
            (labeled-oneof inform_beverage__finish
                (outcome finish
                    (and
                        (force-statement)
                        (informed)
                    )
                )
            )
    )
    (:action inform_cocktail
        :parameters()
        :precondition
            (and
                (know__payment)
                (not (require_drink_ingredients))
                (know__require_drink_ingredients)
                (know__glass)
                (know__mixer)
                (know__size)
                (know__liquor)
                (not (informed))
                (know__drink)
                (not (force-statement))
            )
        :effect
            (labeled-oneof inform_cocktail__finish
                (outcome finish
                    (and
                        (force-statement)
                        (informed)
                    )
                )
            )
    )
    (:action complete
        :parameters()
        :precondition
            (and
                (informed)
                (not (force-statement))
            )
        :effect
            (labeled-oneof complete__finish
                (outcome finish
                    (and
                        (goal)
                    )
                )
            )
    )
    (:action dialogue_statement
        :parameters()
        :precondition
            (and
                (force-statement)
            )
        :effect
            (labeled-oneof dialogue_statement__reset
                (outcome lock
                    (and
                        (not (force-statement))
                    )
                )
            )
    )
    (:action slot-fill__get-drink
        :parameters()
        :precondition
            (and
                (not (force-statement))
                (not (know__drink))
            )
        :effect
            (labeled-oneof slot-fill__get-drink__validate-slot-fill
                (outcome drink_found
                    (and
                        (know__drink)
                        (force-statement)
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
    (:action slot-fill__get-size
        :parameters()
        :precondition
            (and
                (not (force-statement))
                (not (know__size))
            )
        :effect
            (labeled-oneof slot-fill__get-size__validate-slot-fill
                (outcome size_found
                    (and
                        (force-statement)
                        (know__size)
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
    (:action slot-fill__get-glass
        :parameters()
        :precondition
            (and
                (not (force-statement))
                (not (know__glass))
            )
        :effect
            (labeled-oneof slot-fill__get-glass__validate-slot-fill
                (outcome glass_found
                    (and
                        (force-statement)
                        (know__glass)
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
    (:action slot-fill__get-payment
        :parameters()
        :precondition
            (and
                (not (know__payment))
                (not (force-statement))
            )
        :effect
            (labeled-oneof slot-fill__get-payment__validate-slot-fill
                (outcome payment_found
                    (and
                        (know__payment)
                        (force-statement)
                    )
                )
                (outcome fallback
                    (and
                        (force-statement)
                    )
                )
            )
    )
)