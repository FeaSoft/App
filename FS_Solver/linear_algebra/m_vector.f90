! Description:
! Definition of a vector.
module m_vector
    implicit none
    
    private
    public t_vector, new_vector
    
    type t_vector
        integer           :: n_vals ! number of values (size)
        real, allocatable :: at(:)  ! values
    contains
        final :: destructor
    end type
    
    interface new_vector
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Vector constructor.
    type(t_vector) function constructor(n_vals) result(self)
        integer, intent(in) :: n_vals ! number of values (size)
        self%n_vals = n_vals
        allocate(self%at(self%n_vals), source=0.0)
    end function
    
    ! Description:
    ! Vector destructor.
    subroutine destructor(self)
        type(t_vector), intent(inout) :: self
        if (allocated(self%at)) deallocate(self%at)
    end subroutine
    
end module
