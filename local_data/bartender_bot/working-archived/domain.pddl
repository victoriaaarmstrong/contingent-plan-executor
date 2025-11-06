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
        (know__drink_preferences)
        (drink_preferences)
        (know__drink_ingredients)
        (drink_ingredients)
        (informed)
        (know__goal)
        (goal)
        (force-statement)
    )
    (:action set-beverage
        :parameters()
        :precondition
            (and
                (not (know__beverage))
                (know__drink_ingredients)
                (drink_preferences)
                (not (force-statement))
                (know__descriptors)
                (know__drink_preferences)
                (know__drink)
            )
        :effect
            (labeled-oneof set-beverage__assign_beverage
                (outcome set-red-wine
                    (and
                        (know__beverage)
                        (not (drink_preferences))
                    )
                )
                (outcome set-white-wine
                    (and
                        (know__beverage)
                        (not (drink_preferences))
                    )
                )
                (outcome set-lager
                    (and
                        (know__beverage)
                        (not (drink_preferences))
                    )
                )
                (outcome set-radler
                    (and
                        (know__beverage)
                        (not (drink_preferences))
                    )
                )
            )
    )
    (:action set-drink-ingredients
        :parameters()
        :precondition
            (and
                (not (know__beverage))
                (not (know__descriptors))
                (not (know__drink_preferences))
                (not (force-statement))
                (not (know__drink_ingredients))
                (know__drink)
            )
        :effect
            (labeled-oneof set-drink-ingredients__assign_drink_ingredients
                (outcome set-cocktail
                    (and
                        (know__drink_preferences)
                        (know__drink_ingredients)
                        (not (drink_preferences))
                        (drink_ingredients)
                    )
                )
                (outcome set-wine
                    (and
                        (know__drink_preferences)
                        (know__drink_ingredients)
                        (drink_preferences)
                        (not (drink_ingredients))
                    )
                )
                (outcome set-beer
                    (and
                        (know__drink_preferences)
                        (know__drink_ingredients)
                        (drink_preferences)
                        (not (drink_ingredients))
                    )
                )
            )
    )
    (:action get-liquor
        :parameters()
        :precondition
            (and
                (know__drink_ingredients)
                (not (force-statement))
                (not (know__liquor))
                (drink_ingredients)
                (know__drink)
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
                (know__drink_ingredients)
                (know__liquor)
                (know__drink)
            )
        :effect
            (labeled-oneof get-mixer__set-mixer
                (outcome update_mixer
                    (and
                        (know__mixer)
                        (not (drink_ingredients))
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
                (not (know__descriptors))
                (drink_preferences)
                (not (force-statement))
                (know__drink_preferences)
                (know__drink)
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
    (:action inform
        :parameters()
        :precondition
            (and
                (know__glass)
                (know__drink_ingredients)
                (not (force-statement))
                (not (know__payment))
                (not (drink_preferences))
                (know__size)
                (not (informed))
                (know__drink_preferences)
                (know__drink)
                (not (drink_ingredients))
            )
        :effect
            (labeled-oneof inform__finish
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
                (not (force-statement))
                (know__payment)
                (informed)
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
                (not (know__drink))
                (not (force-statement))
            )
        :effect
            (labeled-oneof slot-fill__get-drink__validate-slot-fill
                (outcome drink_found
                    (and
                        (force-statement)
                        (know__drink)
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
                (not (force-statement))
                (not (know__payment))
            )
        :effect
            (labeled-oneof slot-fill__get-payment__validate-slot-fill
                (outcome payment_found
                    (and
                        (force-statement)
                        (know__payment)
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