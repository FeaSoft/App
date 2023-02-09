! Description:
! Definition of a material.
module m_material
    implicit none
    
    private
    public t_material, new_material
    
    type t_material
        real :: young   ! Young's modulus
        real :: poisson ! Poisson's ratio
        real :: density ! mass density
    end type
    
    interface new_material
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Material constructor.
    type(t_material) function constructor(young, poisson, density) result(self)
        real, intent(in) :: young   ! Young's modulus
        real, intent(in) :: poisson ! Poisson's ratio
        real, intent(in) :: density ! mass density
        self%young   = young
        self%poisson = poisson
        self%density = density
    end function
    
end module
